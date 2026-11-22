"""Centro de notificaciones (`001`, "Actualización: centro de notificaciones y
avisos por correo").

Solo lectura: arma las secciones de la campana a partir del estado actual de
Inventario, Ventas, Compras, Facturación y RRHH. No hay tabla de
notificaciones: un aviso desaparece solo cuando se resuelve lo que lo causa.
La misma función alimenta el endpoint de la campana y el resumen diario por
correo.
"""

from decimal import Decimal

from django.db.models import DecimalField, ExpressionWrapper, F
from django.utils import timezone

from apps.compras.models import Compra
from apps.facturacion.models import Factura
from apps.inventario.models import (
    InventarioSucursalMateriaPrima,
    InventarioSucursalProducto,
)
from apps.reportes.services import ESTADOS_FACTURA_VIGENTE, _pagado_con_complementos
from apps.rrhh.models import ESTADO_NOMINA_PENDIENTE, SolicitudNomina
from apps.ventas.models import Venta

LIMITE_POR_SECCION = 5
CERO = Decimal('0.00')

ESTADOS_FACTURA_REQUIEREN_ACCION = [Factura.ESTADO_ERROR, Factura.ESTADO_PENDIENTE_CANCELACION]
ETIQUETA_ESTADO_FACTURA = {
    Factura.ESTADO_ERROR: 'Error de timbrado',
    Factura.ESTADO_PENDIENTE_CANCELACION: 'Cancelación pendiente',
}


def _fecha_corta(fecha):
    return fecha.strftime('%d/%m/%Y')


def _moneda(valor):
    return f'${valor:,.2f}'


def _cantidad(valor):
    return f'{valor:,.2f}'.rstrip('0').rstrip('.')


def _seccion(clave, titulo, ruta, elementos, total, requieren_accion):
    return {
        'clave': clave,
        'titulo': titulo,
        'ruta': ruta,
        'total': total,
        'requieren_accion': requieren_accion,
        'elementos': elementos[:LIMITE_POR_SECCION],
    }


# --- Secciones ---------------------------------------------------------------


def _seccion_stock():
    """Productos y materia prima bajo su mínimo, en cualquier sucursal (toda
    la empresa para ambos roles). Todas requieren acción; primero las de menor
    stock."""

    productos = InventarioSucursalProducto.objects.select_related('producto', 'sucursal').filter(
        stock_actual__lt=F('stock_minimo'),
    )
    materias = InventarioSucursalMateriaPrima.objects.select_related('materia_prima', 'sucursal').filter(
        stock_actual__lt=F('stock_minimo'),
    )
    filas = [(item.producto.nombre_producto, item) for item in productos] + [
        (item.materia_prima.nombre_item, item) for item in materias
    ]
    filas.sort(key=lambda fila: (fila[1].stock_actual, fila[0]))

    elementos = [
        {
            'titulo': nombre,
            'detalle': f'{item.sucursal.nombre_sucursal} · {_cantidad(item.stock_actual)} de {_cantidad(item.stock_minimo)} mínimo',
            'etiqueta': None,
            'urgente': True,
            'ruta': '/inventario',
        }
        for nombre, item in filas
    ]
    return _seccion('stock', 'Stock', '/inventario', elementos, len(filas), len(filas))


def _pendientes_con_entrega(queryset, numero, contraparte, ruta_detalle):
    """Elementos de ventas por entregar / compras por recibir: vencidos
    primero (su `fecha_entrega` ya pasó), luego por fecha más próxima; sin
    fecha, al final."""

    hoy = timezone.localdate()
    ordenados = queryset.order_by(F('fecha_entrega').asc(nulls_last=True), 'id')
    vencidas = queryset.filter(fecha_entrega__lt=hoy).count()

    elementos = []
    for registro in ordenados[:LIMITE_POR_SECCION]:
        vencida = registro.fecha_entrega is not None and registro.fecha_entrega < hoy
        entrega = (
            f'Entrega {_fecha_corta(registro.fecha_entrega)}' if registro.fecha_entrega else 'Sin fecha de entrega'
        )
        etiqueta = None
        if vencida:
            dias = (hoy - registro.fecha_entrega).days
            etiqueta = f'Vencida · hace {dias} día' + ('' if dias == 1 else 's')
        elementos.append({
            'titulo': f'{numero} #{registro.id}',
            'detalle': f'{contraparte(registro)} · {entrega}',
            'etiqueta': etiqueta,
            'urgente': vencida,
            'ruta': f'{ruta_detalle}/{registro.id}',
        })
    return elementos, queryset.count(), vencidas


def _seccion_ventas(usuario):
    ventas = Venta.objects.select_related('cliente').filter(estado=Venta.ESTADO_PENDIENTE)
    if usuario is not None:
        ventas = ventas.filter(usuario=usuario)
    elementos, total, vencidas = _pendientes_con_entrega(
        ventas, 'Venta', lambda venta: venta.cliente.nombre_cliente if venta.cliente else 'Sin cliente', '/ventas',
    )
    return _seccion('ventas', 'Ventas por entregar', '/ventas', elementos, total, vencidas)


def _seccion_compras(usuario):
    compras = Compra.objects.select_related('proveedor').filter(estado=Compra.ESTADO_PENDIENTE)
    if usuario is not None:
        compras = compras.filter(usuario=usuario)
    elementos, total, vencidas = _pendientes_con_entrega(
        compras, 'Compra', lambda compra: compra.proveedor.nombre_proveedor, '/compras',
    )
    return _seccion('compras', 'Compras por recibir', '/compras', elementos, total, vencidas)


def _folio(factura):
    if factura.serie and factura.folio_interno is not None:
        return f'{factura.serie}-{factura.folio_interno}'
    return f'Factura #{factura.id}'


def _seccion_facturas(usuario):
    """Facturas en `error` o `pendiente_cancelacion` (requieren acción) y
    vigentes PPD con saldo por cobrar (total menos complementos timbrados,
    mismo cálculo que `019`), sin repetir una factura que esté en ambos
    grupos."""

    facturas = Factura.objects.select_related('venta__cliente')
    if usuario is not None:
        facturas = facturas.filter(venta__usuario=usuario)

    por_atender = list(facturas.filter(estado__in=ESTADOS_FACTURA_REQUIEREN_ACCION).order_by('estado', '-fecha_creacion'))
    por_cobrar = list(
        facturas.filter(estado__in=ESTADOS_FACTURA_VIGENTE, metodo_pago=Factura.METODO_PPD)
        .annotate(pagado=_pagado_con_complementos())
        .annotate(saldo=ExpressionWrapper(F('venta__total') - F('pagado'), output_field=DecimalField(max_digits=12, decimal_places=2)))
        .filter(saldo__gt=0)
        .order_by('fecha_timbrado', 'id')
    )

    elementos = {}
    for factura in por_atender:
        elementos[factura.id] = {
            'titulo': _folio(factura),
            'detalle': factura.venta.cliente.nombre_cliente if factura.venta.cliente else 'Sin cliente',
            'etiqueta': ETIQUETA_ESTADO_FACTURA[factura.estado],
            'urgente': True,
            'ruta': f'/facturacion/{factura.id}',
        }
    for factura in por_cobrar:
        if factura.id in elementos:
            continue
        elementos[factura.id] = {
            'titulo': _folio(factura),
            'detalle': factura.venta.cliente.nombre_cliente if factura.venta.cliente else 'Sin cliente',
            'etiqueta': f'Por cobrar {_moneda(factura.saldo)}',
            'urgente': False,
            'ruta': f'/facturacion/{factura.id}',
        }

    lista = list(elementos.values())
    return _seccion('facturas', 'Facturas por atender', '/facturacion', lista, len(lista), len(por_atender))


def _seccion_nominas():
    solicitudes = SolicitudNomina.objects.select_related('empleado').filter(
        estado=ESTADO_NOMINA_PENDIENTE,
    ).order_by('fecha_solicitud')
    elementos = [
        {
            'titulo': solicitud.empleado.nombre_completo,
            'detalle': (
                f'{_fecha_corta(solicitud.periodo_inicio)} – {_fecha_corta(solicitud.periodo_fin)} · '
                f'{_moneda(solicitud.monto)}'
            ),
            'etiqueta': None,
            'urgente': True,
            'ruta': '/rrhh?pestana=nominas',
        }
        for solicitud in solicitudes[:LIMITE_POR_SECCION]
    ]
    total = solicitudes.count()
    return _seccion('nominas', 'Nóminas', '/rrhh?pestana=nominas', elementos, total, total)


def armar_notificaciones(usuario=None, incluir_nominas=True) -> dict:
    """Secciones de la campana y su contador.

    `usuario=None` es toda la empresa (admin y resumen diario); con un usuario
    (operador), ventas, compras y facturas se limitan a las suyas — mismo
    criterio de propiedad que los módulos. El stock es de toda la empresa
    para ambos roles. El contador suma solo lo que requiere acción.
    """

    secciones = [_seccion_stock(), _seccion_ventas(usuario), _seccion_compras(usuario), _seccion_facturas(usuario)]
    if incluir_nominas:
        secciones.append(_seccion_nominas())

    return {
        'contador': sum(seccion['requieren_accion'] for seccion in secciones),
        'secciones': [seccion for seccion in secciones if seccion['total'] > 0],
    }
