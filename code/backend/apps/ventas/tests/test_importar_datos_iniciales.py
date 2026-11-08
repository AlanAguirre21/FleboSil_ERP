"""Comando `importar_datos_iniciales` — feature 022 · Carga de datos iniciales."""

import datetime as dt
from decimal import Decimal
from zoneinfo import ZoneInfo

import openpyxl
import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.caja.models import MovimientoCaja
from apps.caja.services import calcular_saldo_actual
from apps.catalogo.models import Producto
from apps.contabilidad.models import AsientoContable
from apps.inventario.models import InventarioSucursalProducto, MovimientoInventario
from apps.sucursales.models import Sucursal
from apps.terceros.models import Cliente
from apps.usuarios.models import Usuario
from apps.ventas.models import DetalleVenta, Venta

ZONA = ZoneInfo('America/Mexico_City')


@pytest.fixture
def usuario(db):
    return Usuario.objects.create_user(username='admin', email='admin@flebosil.test', password='clave-segura-123')


def _ventas_xlsx(ruta, ventas=None, detalle=None, balance='1000.00', saldo_real='1925.00'):
    libro = openpyxl.Workbook()
    libro.remove(libro.active)
    ws = libro.create_sheet('Ventas')
    ws.append(['Folio', 'Fecha', 'Cliente', 'Canal', 'Comprador (marketplace)', 'Ciudad', 'Tipo', 'Estado',
               'Pagado', 'Líneas', 'Piezas', 'Productos', 'Gasto de envío', 'Total', 'Nota', 'Origen'])
    for fila in ventas or [
        ['H-00001', dt.date(2025, 4, 21), 'Dra. Jessica González', 'Directo', None, None, 'Venta',
         'entregada', 'Sí', 2, 25, 900, 0, 900, None, 'ABR.25!60'],
        ['H-00002', dt.date(2025, 5, 2), 'Mercado Libre', 'Mercado Libre', 'Ana', 'CDMX', 'Venta',
         'entregada', 'Sí', 1, 1, 25, 0, 25, None, 'MAY_25!10'],
        ['H-00003', dt.date(2025, 5, 3), 'Mercado Libre', 'Mercado Libre', None, None, 'Obsequio',
         'entregada', 'N/A', 1, 1, 0, 0, 0, None, 'MAY_25!11'],
    ]:
        ws.append(fila)
    ws = libro.create_sheet('Detalle')
    ws.append(['Folio', 'Fecha', 'SKU', 'Producto', 'Cantidad', 'Precio unitario', 'Subtotal', 'Nombre original',
               'Origen'])
    for fila in detalle or [
        ['H-00001', None, 'FS-CALM', 'Calm', 20, 40, 800, None, 'ABR.25!60'],
        ['H-00001', None, 'FS-NUTRITIV', 'Nutritiv', 5, 20, 100, None, 'ABR.25!61'],
        ['H-00002', None, 'FS-CALM', 'Calm', 1, 25, 25, None, 'MAY_25!10'],
        ['H-00003', None, 'FS-CALM', 'Calm', 1, 0, 0, None, 'MAY_25!11'],
    ]:
        ws.append(fila)
    ws = libro.create_sheet('Clientes')
    ws.append(['Cliente', 'Canal'])
    ws.append(['Dra. Jessica González', 'Directo'])
    ws.append(['Mercado Libre', 'Mercado Libre'])
    ws = libro.create_sheet('Caja')
    ws.append(['Fecha', 'Tipo de movimiento', 'Motivo', 'Monto', 'Observación', 'Saldo resultante'])
    ws.append([dt.date(2025, 1, 1), 'ingreso', 'manual', float(balance), 'Balance de caja con total real', None])
    ws.append([])
    ws.append(['Saldo real de caja', None, None, float(saldo_real)])
    libro.save(ruta)
    return str(ruta)


def _inventario_xlsx(ruta):
    libro = openpyxl.Workbook()
    libro.remove(libro.active)
    ws = libro.create_sheet('Productos')
    ws.append(['SKU', 'Nombre del producto', 'Categoría', 'Tipo', 'Unidad de medida', 'Precio de venta sugerido'])
    ws.append(['FS-CALM', 'FleboSil-Calm, Gel Tópico', 'FleboSil', 'Propio', 'Pieza', 175])
    ws.append(['FS-NUTRITIV', 'FleboSil-Nutritiv, Crema Nutritiva', 'FleboSil', 'Propio', 'Pieza', 220])
    ws.append(['CO-001', 'Jobst Opaque 15-20 Panty G beige', 'Compresión', 'Reventa', 'Pieza', 1500])
    ws = libro.create_sheet('Inventario')
    ws.append(['SKU', 'Producto', 'Sucursal', 'Fecha de inicio', 'Existencia de inicio', 'Ingreso (producción)',
               'Venta después del conteo', 'Existencia actual'])
    ws.append(['FS-CALM', 'Calm', 'Consultorio', dt.date(2026, 10, 23), 63, 0, 0, '=E2+F2-G2'])
    ws.append(['FS-NUTRITIV', 'Nutritiv', 'Consultorio', dt.date(2026, 10, 23), 62, 0, 0, '=E3+F3-G3'])
    ws.append(['TOTAL', None, None, None, '=SUM(E2:E3)'])
    libro.save(ruta)
    return str(ruta)


def _importar(tmp_path, **kwargs):
    ventas = kwargs.pop('ventas_xlsx', None) or _ventas_xlsx(tmp_path / 'ventas.xlsx')
    call_command('importar_datos_iniciales', ventas=ventas, inventario=_inventario_xlsx(tmp_path / 'inv.xlsx'),
                 usuario='admin@flebosil.test', interactive=False, **kwargs)


@pytest.mark.django_db
def test_carga_completa(tmp_path, usuario):
    _importar(tmp_path)

    assert set(Sucursal.objects.values_list('nombre_sucursal', flat=True)) == {'Consultorio', 'Laboratorio - Matriz'}
    assert Producto.objects.count() == 3
    assert Cliente.objects.count() == 2
    assert Venta.objects.count() == 3
    assert DetalleVenta.objects.count() == 4

    # Precio del archivo (precio especial), no el del catálogo.
    linea = DetalleVenta.objects.get(producto__sku='FS-CALM', venta__total=Decimal('900.00'))
    assert linea.precio_unitario == Decimal('40.00')
    assert linea.subtotal == Decimal('800.00')

    venta = Venta.objects.get(total=Decimal('900.00'))
    assert venta.estado == Venta.ESTADO_ENTREGADA
    assert venta.sucursal.nombre_sucursal == 'Consultorio'


@pytest.mark.django_db
def test_fechas_historicas_en_venta_caja_inventario_y_asientos(tmp_path, usuario):
    _importar(tmp_path)

    venta = Venta.objects.get(total=Decimal('900.00'))
    assert venta.fecha.astimezone(ZONA).date() == dt.date(2025, 4, 21)
    assert venta.fecha_entrega_real == venta.fecha

    ingreso = MovimientoCaja.objects.get(referencia_id=venta.id)
    assert ingreso.fecha == venta.fecha
    assert AsientoContable.objects.get(referencia_id=venta.id).fecha == venta.fecha

    balance = MovimientoCaja.objects.get(observacion='Balance de caja con total real')
    assert balance.fecha.astimezone(ZONA).date() == dt.date(2025, 1, 1)
    assert balance.motivo == MovimientoCaja.MOTIVO_MANUAL

    ajuste = MovimientoInventario.objects.get(item_id=Producto.objects.get(sku='FS-CALM').id)
    assert ajuste.fecha.astimezone(ZONA).date() == dt.date(2026, 10, 23)


@pytest.mark.django_db
def test_caja_balance_y_saldo_final(tmp_path, usuario):
    _importar(tmp_path)

    assert calcular_saldo_actual() == Decimal('1925.00')
    movimientos = list(MovimientoCaja.objects.order_by('id'))
    # Balance primero, después una venta por fecha; el obsequio en $0 no mueve caja.
    assert [m.monto for m in movimientos] == [Decimal('1000.00'), Decimal('900.00'), Decimal('25.00')]
    assert [m.saldo_resultante for m in movimientos] == [Decimal('1000.00'), Decimal('1900.00'), Decimal('1925.00')]


@pytest.mark.django_db
def test_existencias_de_consultorio_sin_descontar_ventas_historicas(tmp_path, usuario):
    _importar(tmp_path)

    consultorio = Sucursal.objects.get(nombre_sucursal='Consultorio')
    stock = {i.producto.sku: i.stock_actual for i in InventarioSucursalProducto.objects.filter(sucursal=consultorio)}
    assert stock == {'FS-CALM': Decimal('63.00'), 'FS-NUTRITIV': Decimal('62.00')}
    assert not MovimientoInventario.objects.filter(motivo=MovimientoInventario.MOTIVO_VENTA).exists()
    assert not InventarioSucursalProducto.objects.filter(sucursal__nombre_sucursal='Laboratorio - Matriz').exists()


@pytest.mark.django_db
def test_fila_invalida_no_guarda_nada(tmp_path, usuario):
    ventas = _ventas_xlsx(tmp_path / 'ventas.xlsx', detalle=[
        ['H-00001', None, 'FS-CALM', 'Calm', 20, 40, 800, None, 'ABR.25!60'],
        ['H-00001', None, 'FS-NUTRITIV', 'Nutritiv', 5, 20, 999, None, 'ABR.25!61'],   # subtotal mal
        ['H-00002', None, 'FS-CALM', 'Calm', 1, 25, 25, None, 'MAY_25!10'],
        ['H-00003', None, 'FS-CALM', 'Calm', 1, 0, 0, None, 'MAY_25!11'],
    ])
    with pytest.raises(CommandError, match='ABR.25!61'):
        _importar(tmp_path, ventas_xlsx=ventas)
    assert not Producto.objects.exists()
    assert not Venta.objects.exists()
    assert not MovimientoCaja.objects.exists()


@pytest.mark.django_db
def test_saldo_real_que_no_cuadra_se_rechaza(tmp_path, usuario):
    ventas = _ventas_xlsx(tmp_path / 'ventas.xlsx', saldo_real='5000.00')
    with pytest.raises(CommandError, match='saldo real'):
        _importar(tmp_path, ventas_xlsx=ventas)
    assert not Venta.objects.exists()


@pytest.mark.django_db
def test_se_niega_con_base_no_vacia(tmp_path, usuario):
    _importar(tmp_path)
    with pytest.raises(CommandError, match='carga inicial'):
        _importar(tmp_path)
    assert Venta.objects.count() == 3


@pytest.mark.django_db
def test_simular_no_deja_nada(tmp_path, usuario):
    _importar(tmp_path, simular=True)
    assert not Producto.objects.exists()
    assert not Venta.objects.exists()
    assert not MovimientoCaja.objects.exists()
    assert not MovimientoInventario.objects.exists()
    assert not Sucursal.objects.exists()


@pytest.mark.django_db
def test_usuario_inexistente(tmp_path, usuario):
    with pytest.raises(CommandError, match='No existe el usuario'):
        call_command('importar_datos_iniciales', ventas=_ventas_xlsx(tmp_path / 'v.xlsx'),
                     inventario=_inventario_xlsx(tmp_path / 'i.xlsx'), usuario='nadie@flebosil.test',
                     interactive=False)
