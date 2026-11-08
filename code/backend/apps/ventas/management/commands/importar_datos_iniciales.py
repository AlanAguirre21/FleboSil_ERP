"""Carga inicial de datos desde los xlsx corregidos — feature 022.

Lee `VENTAS 2025 - corregido.xlsx` (hojas Ventas, Detalle, Clientes, Caja)
e `INVENTARIO PRODUCTOS FleboSil - corregido.xlsx` (hojas Productos,
Inventario) y los carga en una base vacía, todo dentro de una sola
transacción. Las ventas, movimientos de caja, movimientos de inventario y
asientos llevan la fecha histórica del archivo; nada de lo creado desde la
app puede hacerlo (los serializers tienen `fecha` de solo lectura).
"""

import datetime as dt
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from zoneinfo import ZoneInfo

import openpyxl
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction

from apps.caja.models import MovimientoCaja
from apps.caja.services import calcular_saldo_actual, registrar_movimiento_caja
from apps.catalogo.models import Categoria, Producto
from apps.inventario.models import MovimientoInventario
from apps.inventario.services import (
    bloquear_inventario_producto,
    registrar_movimiento_inventario,
)
from apps.sucursales.models import Sucursal
from apps.terceros.models import Cliente
from apps.ventas.models import DetalleVenta, Venta

SUCURSAL_VENTAS = 'Consultorio'
SUCURSALES = (SUCURSAL_VENTAS, 'Laboratorio - Matriz')
OBSERVACION_BALANCE = 'Balance de caja con total real'
CENT = Decimal('0.01')


class ErrorDeFila(CommandError):
    pass


def _decimal(valor, origen, campo):
    if valor is None or valor == '':
        raise ErrorDeFila(f'{origen}: "{campo}" vacío.')
    try:
        return Decimal(str(valor)).quantize(CENT)
    except InvalidOperation as exc:
        raise ErrorDeFila(f'{origen}: "{campo}" no es un número ({valor!r}).') from exc


def _fecha(valor, origen):
    if isinstance(valor, dt.datetime):
        return valor.date()
    if isinstance(valor, dt.date):
        return valor
    raise ErrorDeFila(f'{origen}: fecha inválida ({valor!r}).')


def _filas(libro, hoja):
    """Filas de una hoja como diccionarios por encabezado; se detiene en la
    primera fila vacía o de TOTAL. Cada fila trae su origen `Hoja!fila`."""

    if hoja not in libro.sheetnames:
        raise CommandError(f'Falta la hoja "{hoja}" en el archivo.')
    ws = libro[hoja]
    filas = ws.iter_rows(values_only=True)
    encabezados = [str(x).strip() if x is not None else '' for x in next(filas)]
    for numero, valores in enumerate(filas, start=2):
        if valores[0] is None or str(valores[0]).strip().upper() == 'TOTAL':
            break
        fila = dict(zip(encabezados, valores))
        fila['_origen'] = f'{hoja}!{numero}'
        yield fila


class Command(BaseCommand):
    help = 'Carga inicial (feature 022): catálogo, clientes, ventas históricas, caja e inventario desde los xlsx.'

    def add_arguments(self, parser):
        parser.add_argument('--ventas', required=True, help='Ruta de "VENTAS 2025 - corregido.xlsx".')
        parser.add_argument('--inventario', required=True, help='Ruta de "INVENTARIO PRODUCTOS FleboSil - corregido.xlsx".')
        parser.add_argument('--usuario', required=True, help='Correo del usuario que queda como autor de los registros.')
        parser.add_argument('--simular', action='store_true', help='Hace toda la carga, muestra el resumen y la deshace.')
        parser.add_argument('--noinput', action='store_false', dest='interactive', help='No pedir confirmación.')

    # ------------------------------------------------------------------ entrada
    def handle(self, *args, **opciones):
        self.zona = ZoneInfo(settings.TIME_ZONE)
        usuario = get_user_model().objects.filter(email__iexact=opciones['usuario']).first()
        if usuario is None:
            raise CommandError(f'No existe el usuario {opciones["usuario"]}.')

        if Venta.objects.exists() or MovimientoCaja.objects.exists() or MovimientoInventario.objects.exists():
            raise CommandError(
                'La base ya tiene ventas o movimientos de caja/inventario: este comando solo sirve para la carga inicial.',
            )

        datos = self._leer(opciones['ventas'], opciones['inventario'])

        bd = connection.settings_dict
        self.stdout.write(f'Base de datos: {bd.get("NAME")} en {bd.get("HOST") or "localhost"}:{bd.get("PORT") or 5432}')
        if opciones['simular']:
            self.stdout.write('Modo simulación: al final se deshace todo.')
        elif opciones['interactive'] and input('Escribe "si" para cargar los datos: ').strip().lower() != 'si':
            raise CommandError('Carga cancelada.')

        with transaction.atomic():
            resumen = self._cargar(datos, usuario)
            self._mostrar(resumen)
            if opciones['simular']:
                transaction.set_rollback(True)
                self.stdout.write(self.style.WARNING('Simulación terminada: no se guardó nada.'))
                return
        self.stdout.write(self.style.SUCCESS('Carga inicial terminada.'))

    def _momento(self, fecha):
        # Solo se conoce el día: mediodía local para que la conversión a UTC no lo cambie.
        return dt.datetime.combine(fecha, dt.time(12, 0), tzinfo=self.zona)

    # ------------------------------------------------------------------ lectura
    def _leer(self, ruta_ventas, ruta_inventario):
        try:
            libro_ventas = openpyxl.load_workbook(ruta_ventas, data_only=True, read_only=True)
            libro_inv = openpyxl.load_workbook(ruta_inventario, data_only=True, read_only=True)
        except (OSError, ValueError) as exc:
            raise CommandError(f'No se pudo abrir el archivo: {exc}') from exc

        productos = []
        for f in _filas(libro_inv, 'Productos'):
            productos.append({
                'sku': str(f['SKU']).strip(), 'nombre': str(f['Nombre del producto']).strip(),
                'categoria': str(f['Categoría']).strip(), 'unidad': str(f.get('Unidad de medida') or 'Pieza').strip(),
                'precio': _decimal(f['Precio de venta sugerido'], f['_origen'], 'Precio de venta sugerido'),
            })
        skus = {p['sku'] for p in productos}
        if len(skus) != len(productos):
            raise CommandError('Productos: hay SKU repetidos.')

        existencias = []
        for f in _filas(libro_inv, 'Inventario'):
            sku = str(f['SKU']).strip()
            if sku not in skus:
                raise ErrorDeFila(f'{f["_origen"]}: SKU {sku} no está en Productos.')
            cantidad = (_decimal(f['Existencia de inicio'], f['_origen'], 'Existencia de inicio')
                        + _decimal(f.get('Ingreso (producción)') or 0, f['_origen'], 'Ingreso')
                        - _decimal(next((v for k, v in f.items() if k.startswith('Venta')), 0) or 0,
                                   f['_origen'], 'Venta'))
            if cantidad < 0:
                raise ErrorDeFila(f'{f["_origen"]}: existencia negativa ({cantidad}).')
            existencias.append({'sku': sku, 'sucursal': str(f['Sucursal']).strip(), 'cantidad': cantidad,
                                'fecha': _fecha(f['Fecha de inicio'], f['_origen'])})

        clientes = [str(f['Cliente']).strip() for f in _filas(libro_ventas, 'Clientes')]

        detalles = defaultdict(list)
        for f in _filas(libro_ventas, 'Detalle'):
            origen = f'{f["_origen"]} ({f.get("Origen")})'
            sku = str(f['SKU']).strip()
            if sku not in skus:
                raise ErrorDeFila(f'{origen}: SKU {sku} no está en Productos.')
            cantidad = _decimal(f['Cantidad'], origen, 'Cantidad')
            precio = _decimal(f['Precio unitario'], origen, 'Precio unitario')
            subtotal = _decimal(f['Subtotal'], origen, 'Subtotal')
            if cantidad <= 0 or precio < 0:
                raise ErrorDeFila(f'{origen}: cantidad o precio inválidos.')
            # En los kits repartidos el precio unitario se redondeó al centavo y el
            # subtotal conserva el importe exacto: se tolera medio centavo por pieza.
            if abs(cantidad * precio - subtotal) > max(CENT, cantidad * Decimal('0.005')):
                raise ErrorDeFila(f'{origen}: subtotal {subtotal} ≠ {cantidad} × {precio}.')
            detalles[str(f['Folio']).strip()].append({'sku': sku, 'cantidad': cantidad, 'precio': precio,
                                                      'subtotal': subtotal})

        ventas = []
        for f in _filas(libro_ventas, 'Ventas'):
            origen = f['_origen']
            folio = str(f['Folio']).strip()
            lineas = detalles.pop(folio, None)
            if not lineas:
                raise ErrorDeFila(f'{origen}: la venta {folio} no tiene líneas en Detalle.')
            envio = _decimal(f.get('Gasto de envío') or 0, origen, 'Gasto de envío')
            total = _decimal(f['Total'], origen, 'Total')
            if envio < 0:
                raise ErrorDeFila(f'{origen}: gasto de envío negativo.')
            if sum(linea['subtotal'] for linea in lineas) + envio != total:
                raise ErrorDeFila(f'{origen}: el total {total} no es la suma de sus líneas más el envío.')
            estado = str(f['Estado']).strip()
            if estado not in (Venta.ESTADO_ENTREGADA, Venta.ESTADO_PENDIENTE):
                raise ErrorDeFila(f'{origen}: estado desconocido "{estado}".')
            cliente = str(f['Cliente']).strip()
            if cliente not in clientes:
                raise ErrorDeFila(f'{origen}: el cliente "{cliente}" no está en la hoja Clientes.')
            ventas.append({'folio': folio, 'fecha': _fecha(f['Fecha'], origen), 'cliente': cliente,
                           'estado': estado, 'envio': envio, 'total': total, 'lineas': lineas})
        if detalles:
            raise CommandError(f'Detalle tiene líneas de ventas inexistentes: {", ".join(sorted(detalles)[:5])}.')

        balance, saldo_real = None, None
        ws_caja = libro_ventas['Caja'] if 'Caja' in libro_ventas.sheetnames else None
        if ws_caja is None:
            raise CommandError('Falta la hoja "Caja" en el archivo de ventas.')
        for valores in ws_caja.iter_rows(values_only=True):
            if not valores:
                continue
            if len(valores) > 4 and valores[4] == OBSERVACION_BALANCE:
                balance = {'fecha': _fecha(valores[0], 'Caja'), 'monto': _decimal(valores[3], 'Caja', 'Monto')}
            if valores[0] == 'Saldo real de caja':
                saldo_real = _decimal(valores[3], 'Caja', 'Saldo real de caja')
        if balance is None or saldo_real is None:
            raise CommandError(f'La hoja Caja debe traer el movimiento "{OBSERVACION_BALANCE}" y el "Saldo real de caja".')
        esperado = balance['monto'] + sum(v['total'] for v in ventas)
        if esperado != saldo_real:
            raise CommandError(f'Caja: balance + ventas = {esperado}, pero el saldo real es {saldo_real}.')

        ventas.sort(key=lambda v: (v['fecha'], v['folio']))
        return {'productos': productos, 'existencias': existencias, 'clientes': clientes, 'ventas': ventas,
                'balance': balance, 'saldo_real': saldo_real}

    # -------------------------------------------------------------------- carga
    def _cargar(self, datos, usuario):
        sucursales = {}
        for nombre in SUCURSALES:
            sucursales[nombre], _ = Sucursal.objects.get_or_create(nombre_sucursal=nombre)

        categorias, productos = {}, {}
        for p in datos['productos']:
            if p['categoria'] not in categorias:
                categorias[p['categoria']], _ = Categoria.objects.get_or_create(
                    nombre_categoria=p['categoria'], defaults={'tipo': Categoria.TIPO_PRODUCTO},
                )
            productos[p['sku']], _ = Producto.objects.get_or_create(
                sku=p['sku'],
                defaults={'nombre_producto': p['nombre'], 'unidad_medida': p['unidad'],
                          'categoria': categorias[p['categoria']], 'precio_venta': p['precio']},
            )

        clientes = {}
        for nombre in datos['clientes']:
            clientes[nombre] = (Cliente.objects.filter(nombre_cliente=nombre).first()
                                or Cliente.objects.create(nombre_cliente=nombre))

        # Caja: primero el balance previo a los archivos, luego cada venta en
        # orden cronológico — `saldo_resultante` se arrastra por `id`.
        registrar_movimiento_caja(
            tipo_movimiento=MovimientoCaja.INGRESO, monto=datos['balance']['monto'], motivo=MovimientoCaja.MOTIVO_MANUAL,
            referencia_id=None, usuario=usuario, observacion=OBSERVACION_BALANCE,
            fecha=self._momento(datos['balance']['fecha']),
        )

        sucursal = sucursales[SUCURSAL_VENTAS]
        for v in datos['ventas']:
            momento = self._momento(v['fecha'])
            venta = Venta.objects.create(
                cliente=clientes[v['cliente']], sucursal=sucursal, usuario=usuario, fecha=momento,
                fecha_entrega_real=momento if v['estado'] == Venta.ESTADO_ENTREGADA else None,
                total=v['total'], gasto_envio=v['envio'], estado=v['estado'],
            )
            DetalleVenta.objects.bulk_create([
                DetalleVenta(venta=venta, producto=productos[linea['sku']], cantidad=linea['cantidad'],
                             precio_unitario=linea['precio'], subtotal=linea['subtotal'])
                for linea in v['lineas']
            ])
            # Mismo reparto que `VentaViewSet.create`: productos con motivo
            # `venta` y envío aparte; una venta en $0 (obsequio) no mueve caja.
            if v['total'] - v['envio'] > 0:
                registrar_movimiento_caja(
                    tipo_movimiento=MovimientoCaja.INGRESO, monto=v['total'] - v['envio'],
                    motivo=MovimientoCaja.MOTIVO_VENTA, referencia_id=venta.id, usuario=usuario,
                    observacion=f'Venta #{venta.id} (histórica {v["folio"]})', fecha=momento,
                )
            if v['envio'] > 0:
                registrar_movimiento_caja(
                    tipo_movimiento=MovimientoCaja.INGRESO, monto=v['envio'], motivo=MovimientoCaja.MOTIVO_ENVIO,
                    referencia_id=venta.id, usuario=usuario, observacion=f'Envío de venta #{venta.id}', fecha=momento,
                )

        # Existencias contadas: entrada de ajuste con la fecha del conteo. Las
        # ventas históricas no descuentan stock (el conteo es posterior).
        for e in datos['existencias']:
            if e['cantidad'] <= 0:
                continue
            if e['sucursal'] not in sucursales:
                sucursales[e['sucursal']], _ = Sucursal.objects.get_or_create(nombre_sucursal=e['sucursal'])
            inventario = bloquear_inventario_producto(sucursales[e['sucursal']], productos[e['sku']])
            inventario.stock_actual += e['cantidad']
            inventario.save(update_fields=['stock_actual'])
            registrar_movimiento_inventario(
                sucursal=sucursales[e['sucursal']], tipo_item=MovimientoInventario.TIPO_PRODUCTO,
                item_id=productos[e['sku']].id, tipo_movimiento=MovimientoInventario.ENTRADA, cantidad=e['cantidad'],
                motivo=MovimientoInventario.MOTIVO_AJUSTE, referencia_id=None,
                stock_resultante=inventario.stock_actual, usuario=usuario, fecha=self._momento(e['fecha']),
            )

        saldo = calcular_saldo_actual()
        if saldo != datos['saldo_real']:
            raise CommandError(f'El saldo de caja quedó en {saldo}, no en {datos["saldo_real"]}.')
        return {
            'productos': len(productos), 'clientes': len(clientes), 'ventas': len(datos['ventas']),
            'lineas': sum(len(v['lineas']) for v in datos['ventas']),
            'vendido': sum(v['total'] for v in datos['ventas']), 'balance': datos['balance']['monto'],
            'saldo': saldo, 'existencias': [(e['sku'], e['sucursal'], e['cantidad']) for e in datos['existencias']],
        }

    def _mostrar(self, r):
        self.stdout.write(f'Productos: {r["productos"]} | Clientes: {r["clientes"]}')
        self.stdout.write(f'Ventas: {r["ventas"]} | Líneas: {r["lineas"]} | Total vendido: ${r["vendido"]:,}')
        self.stdout.write(f'Balance de caja: ${r["balance"]:,} | Saldo de caja: ${r["saldo"]:,}')
        self.stdout.write('Existencias:')
        for sku, sucursal, cantidad in r['existencias']:
            self.stdout.write(f'  {sku:<14} {sucursal:<14} {cantidad}')
