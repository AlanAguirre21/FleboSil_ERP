"""Agregación de solo lectura sobre `Venta`/`Compra`/`MovimientoCaja`/
`Produccion` para el panel de reportes del Dashboard (`016`) — no crea ni
modifica ningún modelo, solo `Sum()`/`Count()` sobre tablas ya existentes.
"""

import calendar
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from decimal import Decimal

from django.db.models import (
    Count,
    DecimalField,
    OuterRef,
    QuerySet,
    Subquery,
    Sum,
    Value,
)
from django.db.models.functions import Coalesce
from django.utils import timezone

from apps.caja.models import MovimientoCaja
from apps.compras.models import Compra, DetalleCompraMateriaPrima, DetalleCompraProducto
from apps.facturacion.models import ComplementoPago, Factura
from apps.produccion.models import Produccion
from apps.ventas.models import DetalleVenta, Venta

PERIODO_DIA = 'dia'
PERIODO_SEMANA = 'semana'
PERIODO_MES = 'mes'
PERIODO_ANIO = 'año'
# Rango a elección (`016`, "Actualización: periodos ampliados, comparación y
# producción") — solo admin.
PERIODO_PERSONALIZADO = 'personalizado'
PERIODOS_VALIDOS = [
    PERIODO_DIA,
    PERIODO_SEMANA,
    PERIODO_MES,
    PERIODO_ANIO,
    PERIODO_PERSONALIZADO,
]
# Periodos de calendario: el periodo anterior es el mismo tramo del periodo
# previo (de su inicio hasta el mismo punto), no el periodo previo completo.
PERIODOS_CALENDARIO = [PERIODO_DIA, PERIODO_SEMANA, PERIODO_MES, PERIODO_ANIO]

# Rango personalizado: máximo 2 años, para acotar las filas que se agrupan
# en Python (`_agrupar_por_bucket`).
MAXIMO_DIAS_PERSONALIZADO = 731

ORDEN_MAS = 'mas'
ORDEN_MENOS = 'menos'
ORDENES_VALIDOS = [ORDEN_MAS, ORDEN_MENOS]

LIMITE_5 = '5'
LIMITE_10 = '10'
LIMITE_TODOS = 'todos'
LIMITES_VALIDOS = [LIMITE_5, LIMITE_10, LIMITE_TODOS]

GRANULARIDAD_HORA = 'hora'
GRANULARIDAD_DIA = 'dia'
GRANULARIDAD_SEMANA = 'semana'
GRANULARIDAD_MES = 'mes'

# Solo cuentan los estados donde la venta/compra ya tuvo un efecto
# económico real sobre el negocio — no simplemente donde existe el
# registro:
# - Venta: `pendiente` y `entregada` cuentan por igual, porque el stock y
#   el ingreso de caja ya se descontaron/registraron al CREAR la venta
#   (011 · Ventas no tiene paso "recibir" separado) — solo `cancelada` se
#   excluye.
# - Compra: `pendiente` y `recibida` cuentan por igual (ajuste "compras en
#   caja" de `013 · Caja`) — el retiro de caja ya ocurre al CREAR la
#   compra, no en `recibir()` (que sigue gobernando solo el efecto sobre
#   inventario/asiento de Inventario-Proveedores) — solo `cancelada` se
#   excluye, mismo criterio que Ventas.
ESTADOS_VENTA_CUENTAN = [Venta.ESTADO_PENDIENTE, Venta.ESTADO_ENTREGADA]
ESTADOS_COMPRA_CUENTAN = [Compra.ESTADO_PENDIENTE, Compra.ESTADO_RECIBIDA]

CERO = Decimal('0.00')
CIEN = Decimal(100)


# --- Rango del periodo ----------------------------------------------------


@dataclass(frozen=True)
class Rango:
    """Rango ya resuelto de una consulta del Dashboard: `inicio`/`fin`
    (con zona horaria, ambos inclusivos), la agrupación de las series y el
    periodo pedido (se devuelve tal cual en las respuestas)."""

    periodo: str
    inicio: datetime
    fin: datetime
    granularidad: str


def _inicio_del_dia(fecha_local):
    return fecha_local.replace(hour=0, minute=0, second=0, microsecond=0)


def _granularidad_por_duracion(dias: int) -> str:
    if dias <= 2:
        return GRANULARIDAD_HORA
    if dias <= 92:
        return GRANULARIDAD_DIA
    if dias <= 366:
        return GRANULARIDAD_SEMANA
    return GRANULARIDAD_MES


def resolver_rango(periodo: str, desde: date | None = None, hasta: date | None = None, ahora=None) -> Rango:
    """Convierte el periodo pedido (y, para `personalizado`, sus fechas ya
    validadas por `ParametrosPeriodoSerializer`) en un `Rango`."""

    ahora = timezone.localtime(ahora) if ahora is not None else timezone.localtime()

    if periodo == PERIODO_DIA:
        return Rango(periodo, _inicio_del_dia(ahora), ahora, GRANULARIDAD_HORA)
    if periodo == PERIODO_SEMANA:
        return Rango(periodo, _inicio_del_dia(ahora - timedelta(days=ahora.weekday())), ahora, GRANULARIDAD_DIA)
    if periodo == PERIODO_MES:
        return Rango(periodo, _inicio_del_dia(ahora.replace(day=1)), ahora, GRANULARIDAD_DIA)
    if periodo == PERIODO_ANIO:
        return Rango(periodo, _inicio_del_dia(ahora.replace(month=1, day=1)), ahora, GRANULARIDAD_MES)
    if periodo == PERIODO_PERSONALIZADO:
        if desde is None or hasta is None:
            raise ValueError('El periodo personalizado requiere `desde` y `hasta`.')
        zona = timezone.get_current_timezone()
        inicio = timezone.make_aware(datetime.combine(desde, time.min), zona)
        # Días completos; si "hasta" es hoy, el rango termina ahora.
        fin = min(timezone.make_aware(datetime.combine(hasta, time.max), zona), ahora)
        return Rango(periodo, inicio, fin, _granularidad_por_duracion((hasta - desde).days + 1))

    raise ValueError(f'Periodo inválido: {periodo!r} — debe ser uno de {PERIODOS_VALIDOS}.')


def _restar_meses(fecha, meses: int):
    """Misma fecha y hora `meses` meses antes; el día se limita al último
    día del mes de destino (31 de marzo → 28/29 de febrero)."""

    total = fecha.year * 12 + (fecha.month - 1) - meses
    anio, mes = divmod(total, 12)
    mes += 1
    dia = min(fecha.day, calendar.monthrange(anio, mes)[1])
    return fecha.replace(year=anio, month=mes, day=dia)


def rango_anterior(rango: Rango) -> Rango:
    """Periodo anterior equivalente, para la comparación de los indicadores.

    - Periodos de calendario: el mismo tramo del periodo previo (de su
      inicio hasta el mismo punto), para que un lunes por la mañana no se
      compare contra una semana completa.
    - Personalizado: la ventana de igual duración que termina justo antes
      de `inicio`.
    """

    def _local(fecha):
        # Vuelve a calcular el desfase horario de la fecha resultante.
        return timezone.make_aware(fecha.replace(tzinfo=None), timezone.get_current_timezone())

    if rango.periodo == PERIODO_DIA:
        return Rango(rango.periodo, _local(rango.inicio - timedelta(days=1)), _local(rango.fin - timedelta(days=1)), rango.granularidad)
    if rango.periodo == PERIODO_SEMANA:
        return Rango(rango.periodo, _local(rango.inicio - timedelta(days=7)), _local(rango.fin - timedelta(days=7)), rango.granularidad)
    if rango.periodo == PERIODO_MES:
        return Rango(rango.periodo, _local(_restar_meses(rango.inicio, 1)), _local(_restar_meses(rango.fin, 1)), rango.granularidad)
    if rango.periodo == PERIODO_ANIO:
        return Rango(rango.periodo, _local(_restar_meses(rango.inicio, 12)), _local(_restar_meses(rango.fin, 12)), rango.granularidad)

    fin = rango.inicio - timedelta(microseconds=1)
    return Rango(rango.periodo, fin - (rango.fin - rango.inicio), fin, rango.granularidad)


def _fechas_del_rango(rango: Rango) -> dict:
    """Inicio y fin del rango en hora local, para que el Dashboard muestre
    con qué fechas se compara cada variación."""
    return {'inicio': timezone.localtime(rango.inicio).isoformat(), 'fin': timezone.localtime(rango.fin).isoformat()}


def _variacion(actual, anterior):
    """Variación porcentual con un decimal, o `None` si el periodo anterior
    es cero (no hay base contra la cual comparar)."""

    if actual is None or not anterior:
        return None
    return ((Decimal(actual) - Decimal(anterior)) * CIEN / abs(Decimal(anterior))).quantize(Decimal('0.1'))


# --- Agrupación por punto ---------------------------------------------------


def _clave_bucket(fecha_local, granularidad):
    if granularidad == GRANULARIDAD_HORA:
        return fecha_local.replace(minute=0, second=0, microsecond=0)
    if granularidad == GRANULARIDAD_MES:
        return _inicio_del_dia(fecha_local.replace(day=1))
    if granularidad == GRANULARIDAD_SEMANA:
        # Semanas de lunes a domingo, identificadas por su lunes.
        return _inicio_del_dia(fecha_local - timedelta(days=fecha_local.weekday()))
    return _inicio_del_dia(fecha_local)


def _siguiente_mes(fecha):
    if fecha.month == 12:
        return fecha.replace(year=fecha.year + 1, month=1)
    return fecha.replace(month=fecha.month + 1)


def _generar_claves(rango: Rango):
    claves = []
    # La primera clave es el punto que contiene a `inicio` (en la agrupación
    # semanal, el lunes de esa semana aunque el rango empiece después).
    cursor = _clave_bucket(timezone.localtime(rango.inicio), rango.granularidad)
    while cursor <= rango.fin:
        claves.append(cursor)
        if rango.granularidad == GRANULARIDAD_HORA:
            cursor += timedelta(hours=1)
        elif rango.granularidad == GRANULARIDAD_MES:
            cursor = _siguiente_mes(cursor)
        elif rango.granularidad == GRANULARIDAD_SEMANA:
            cursor += timedelta(days=7)
        else:
            cursor += timedelta(days=1)
    return claves


def _agrupar_por_bucket(pares_fecha_monto, granularidad):
    """Agrupa pares `(fecha, monto)` ya traídos de la base de datos (no
    todas las columnas ni filas fuera de rango) en Python — con el
    volumen esperado (negocio pequeño) es más simple y evita depender de
    cómo `TruncHour`/`TruncDate` de Django resuelven zona horaria a nivel
    SQL. El rango personalizado se limita a 2 años por la misma razón.
    """

    totales: dict = {}
    for fecha, monto in pares_fecha_monto:
        clave = _clave_bucket(timezone.localtime(fecha), granularidad)
        totales[clave] = totales.get(clave, CERO) + (monto or CERO)
    return totales


def _totales_por_bucket(queryset: QuerySet, granularidad, campo='total'):
    return _agrupar_por_bucket(queryset.values_list('fecha', campo), granularidad)


def _serie_desde_totales(totales_por_bucket, claves, campo='monto'):
    return [{'fecha': clave.isoformat(), campo: totales_por_bucket.get(clave, CERO)} for clave in claves]


def _en_rango(rango: Rango, campo='fecha'):
    return {f'{campo}__gte': rango.inicio, f'{campo}__lte': rango.fin}


# Alcance por usuario (`016`, "Actualización: cifras propias para el
# operador"): `usuario=None` es toda la empresa (admin); con un usuario, solo
# sus ventas, compras y las facturas de sus ventas — mismo criterio de
# propiedad que los módulos de Ventas, Compras y Facturación.
def _por_usuario(manager, campo, usuario):
    consulta = manager.all()
    return consulta.filter(**{campo: usuario}) if usuario is not None else consulta


def _ventas(usuario):
    return _por_usuario(Venta.objects, 'usuario', usuario)


def _compras(usuario):
    return _por_usuario(Compra.objects, 'usuario', usuario)


def _facturas(usuario):
    return _por_usuario(Factura.objects, 'venta__usuario', usuario)


def _ventas_que_cuentan(rango: Rango, usuario):
    return _ventas(usuario).filter(**_en_rango(rango), estado__in=ESTADOS_VENTA_CUENTAN)


def _compras_que_cuentan(rango: Rango, usuario):
    return _compras(usuario).filter(**_en_rango(rango), estado__in=ESTADOS_COMPRA_CUENTAN)


def _totales_ventas_compras(rango: Rango, usuario):
    ventas_total = _ventas_que_cuentan(rango, usuario).aggregate(total=Sum('total'))['total'] or CERO
    compras_total = _compras_que_cuentan(rango, usuario).aggregate(total=Sum('total'))['total'] or CERO
    return ventas_total, compras_total


def calcular_resumen(rango: Rango, usuario=None) -> dict:
    ventas_qs = _ventas_que_cuentan(rango, usuario)
    compras_qs = _compras_que_cuentan(rango, usuario)

    ventas_total, compras_total = _totales_ventas_compras(rango, usuario)
    ganancia = ventas_total - compras_total

    ventas_por_bucket = _totales_por_bucket(ventas_qs, rango.granularidad)
    compras_por_bucket = _totales_por_bucket(compras_qs, rango.granularidad)

    serie = [
        {
            'fecha': clave.isoformat(),
            'ganancia': ventas_por_bucket.get(clave, CERO) - compras_por_bucket.get(clave, CERO),
        }
        for clave in _generar_claves(rango)
    ]

    # Comparación: solo los totales del periodo anterior, no sus series.
    anterior = rango_anterior(rango)
    ventas_anterior, compras_anterior = _totales_ventas_compras(anterior, usuario)
    ganancia_anterior = ventas_anterior - compras_anterior

    return {
        'periodo': rango.periodo,
        'granularidad': rango.granularidad,
        'ventas_total': ventas_total,
        'compras_total': compras_total,
        'ganancia': ganancia,
        'serie': serie,
        'periodo_anterior': _fechas_del_rango(anterior),
        'anterior': {
            'ventas_total': ventas_anterior,
            'compras_total': compras_anterior,
            'ganancia': ganancia_anterior,
        },
        'variacion': {
            'ventas_total': _variacion(ventas_total, ventas_anterior),
            'compras_total': _variacion(compras_total, compras_anterior),
            'ganancia': _variacion(ganancia, ganancia_anterior),
        },
    }


def _numero_y_ticket(rango: Rango, usuario):
    """Número de ventas que cuentan y ticket promedio (`Venta.total`, con
    envío, entre el número de ventas); `None` sin ventas."""

    totales = _ventas_que_cuentan(rango, usuario).aggregate(numero=Count('id'), total=Sum('total'))
    numero = totales['numero'] or 0
    ticket = (totales['total'] / numero).quantize(Decimal('0.01')) if numero else None
    return numero, ticket


def calcular_resumen_ventas(rango: Rango, usuario=None) -> dict:
    """Desglose para la sección 'Resumen de ventas' del Dashboard: series
    con envío / sin envío / solo envío, conteo por estado para la gráfica
    de barras Pendiente/Entregada, y número de ventas y ticket promedio con
    su comparación contra el periodo anterior.
    """

    claves = _generar_claves(rango)
    ventas_qs = _ventas_que_cuentan(rango, usuario)

    con_envio_por_bucket = _totales_por_bucket(ventas_qs, rango.granularidad, campo='total')
    envio_por_bucket = _totales_por_bucket(ventas_qs, rango.granularidad, campo='gasto_envio')
    sin_envio_por_bucket = {
        clave: con_envio_por_bucket.get(clave, CERO) - envio_por_bucket.get(clave, CERO) for clave in claves
    }

    conteo_estado = [
        {
            'tipo': 'Pendiente',
            'cantidad': _ventas(usuario).filter(**_en_rango(rango), estado=Venta.ESTADO_PENDIENTE).count(),
        },
        {
            'tipo': 'Entregada',
            'cantidad': _ventas(usuario).filter(**_en_rango(rango), estado=Venta.ESTADO_ENTREGADA).count(),
        },
    ]

    numero_ventas, ticket_promedio = _numero_y_ticket(rango, usuario)
    anterior = rango_anterior(rango)
    numero_anterior, ticket_anterior = _numero_y_ticket(anterior, usuario)

    return {
        'periodo': rango.periodo,
        'granularidad': rango.granularidad,
        'con_envio': _serie_desde_totales(con_envio_por_bucket, claves),
        'sin_envio': _serie_desde_totales(sin_envio_por_bucket, claves),
        'envio': _serie_desde_totales(envio_por_bucket, claves),
        'conteo_estado': conteo_estado,
        'numero_ventas': numero_ventas,
        'ticket_promedio': ticket_promedio,
        'periodo_anterior': _fechas_del_rango(anterior),
        'anterior': {'numero_ventas': numero_anterior, 'ticket_promedio': ticket_anterior},
        'variacion': {
            'numero_ventas': _variacion(numero_ventas, numero_anterior),
            'ticket_promedio': _variacion(ticket_promedio, ticket_anterior),
        },
    }


def calcular_resumen_compras(rango: Rango, usuario=None) -> dict:
    """Desglose para la sección 'Resumen de compras': series todas /
    productos / insumos, más conteo por estado para la gráfica de barras
    Pendiente/Recibida. Una `Compra` puede incluir líneas de producto y
    de materia prima a la vez, así que el desglose se hace a nivel de
    detalle (`DetalleCompraProducto`/`DetalleCompraMateriaPrima`), no de
    `Compra.total`.
    """

    claves = _generar_claves(rango)

    detalles_producto = _por_usuario(DetalleCompraProducto.objects, 'compra__usuario', usuario).filter(
        **_en_rango(rango, 'compra__fecha'), compra__estado__in=ESTADOS_COMPRA_CUENTAN,
    ).values_list('compra__fecha', 'subtotal')

    detalles_materia_prima = _por_usuario(DetalleCompraMateriaPrima.objects, 'compra__usuario', usuario).filter(
        **_en_rango(rango, 'compra__fecha'), compra__estado__in=ESTADOS_COMPRA_CUENTAN,
    ).values_list('compra__fecha', 'subtotal')

    productos_por_bucket = _agrupar_por_bucket(detalles_producto, rango.granularidad)
    insumos_por_bucket = _agrupar_por_bucket(detalles_materia_prima, rango.granularidad)
    todas_por_bucket = {
        clave: productos_por_bucket.get(clave, CERO) + insumos_por_bucket.get(clave, CERO) for clave in claves
    }

    conteo_estado = [
        {
            'tipo': 'Pendiente',
            'cantidad': _compras(usuario).filter(**_en_rango(rango), estado=Compra.ESTADO_PENDIENTE).count(),
        },
        {
            'tipo': 'Recibida',
            'cantidad': _compras(usuario).filter(**_en_rango(rango), estado=Compra.ESTADO_RECIBIDA).count(),
        },
    ]

    return {
        'periodo': rango.periodo,
        'granularidad': rango.granularidad,
        'todas': _serie_desde_totales(todas_por_bucket, claves),
        'productos': _serie_desde_totales(productos_por_bucket, claves),
        'insumos': _serie_desde_totales(insumos_por_bucket, claves),
        'conteo_estado': conteo_estado,
    }


TOP_PRODUCTOS_POR_CANTIDAD = 'cantidad'
TOP_PRODUCTOS_POR_IMPORTE = 'importe'
TOP_PRODUCTOS_POR_VALIDOS = [TOP_PRODUCTOS_POR_CANTIDAD, TOP_PRODUCTOS_POR_IMPORTE]


def calcular_top_productos(
    rango: Rango, orden: str = ORDEN_MAS, usuario=None, por: str = TOP_PRODUCTOS_POR_CANTIDAD,
) -> list:
    """Top 5 productos por cantidad vendida (`por='cantidad'`) o por importe
    vendido (`por='importe'`, suma de `DetalleVenta.subtotal`, el precio
    congelado en la venta; solo admin). `orden='menos'` solo considera
    productos con ventas en el periodo — nunca lista productos sin ventas,
    que no tendrían un ranking con significado.
    """

    campo_agregado = 'subtotal' if por == TOP_PRODUCTOS_POR_IMPORTE else 'cantidad'
    query = (
        _por_usuario(DetalleVenta.objects, 'venta__usuario', usuario).filter(
            **_en_rango(rango, 'venta__fecha'), venta__estado__in=ESTADOS_VENTA_CUENTAN,
        )
        .values('producto__nombre_producto')
        .annotate(**{por: Sum(campo_agregado)})
        .filter(**{f'{por}__gt': 0})
    )
    query = query.order_by(por if orden == ORDEN_MENOS else f'-{por}', 'producto__nombre_producto')

    return [{'producto': fila['producto__nombre_producto'], por: fila[por]} for fila in query[:5]]


TOP_CLIENTES_POR_MONTO = 'monto'
TOP_CLIENTES_POR_COMPRAS = 'compras'


def calcular_top_clientes(
    rango: Rango, orden: str = ORDEN_MAS, por: str = TOP_CLIENTES_POR_MONTO, usuario=None,
) -> list:
    """Top 5 clientes por monto comprado (`por='monto'`, admin) o por número
    de compras (`por='compras'`, operador: sin importes). Excluye ventas sin
    cliente (venta de mostrador) y, con `orden='menos'`, clientes sin
    compras en el periodo.
    """

    query = _ventas_que_cuentan(rango, usuario).filter(cliente__isnull=False).values('cliente__nombre_cliente')
    if por == TOP_CLIENTES_POR_COMPRAS:
        query = query.annotate(compras=Count('id')).filter(compras__gt=0)
    else:
        query = query.annotate(monto=Sum('total')).filter(monto__gt=0)
    query = query.order_by(por if orden == ORDEN_MENOS else f'-{por}')

    return [{'cliente': fila['cliente__nombre_cliente'], por: fila[por]} for fila in query[:5]]


def obtener_movimientos_caja(rango: Rango, limite: str = LIMITE_10):
    """Movimientos de caja del periodo, más recientes primero. Se usa
    para la lista de 'Movimientos financieros del periodo' del Dashboard
    — a diferencia del endpoint admin-only de `013 · Caja`, el llamador
    decide qué campos exponer (solo fecha/tipo/observación).
    """

    queryset = MovimientoCaja.objects.filter(**_en_rango(rango)).order_by('-fecha')

    if limite == LIMITE_TODOS:
        return queryset

    return queryset[: int(limite)]


# --- Resumen producción (`016`, "Actualización: periodos ampliados,
# comparación y producción")


def calcular_resumen_produccion(rango: Rango, incluir_costo: bool = True, usuario=None) -> dict:
    """Sección 'Resumen de producción'. Con `usuario` (operador), solo sus
    producciones, igual que el módulo Producción. El costo (materia prima
    congelada al producir) es información financiera: solo se incluye
    para el admin.
    """

    producciones_qs = _por_usuario(Produccion.objects, 'usuario', usuario).filter(**_en_rango(rango))
    totales = producciones_qs.aggregate(
        producciones=Count('id'), unidades=Sum('cantidad_producida'), costo=Sum('costo_total'),
    )

    claves = _generar_claves(rango)
    unidades_por_bucket = _totales_por_bucket(producciones_qs, rango.granularidad, campo='cantidad_producida')

    top_productos = (
        producciones_qs.values('producto__nombre_producto')
        .annotate(cantidad=Sum('cantidad_producida'))
        .filter(cantidad__gt=0)
        .order_by('-cantidad', 'producto__nombre_producto')[:5]
    )

    resumen = {
        'periodo': rango.periodo,
        'granularidad': rango.granularidad,
        'producciones': totales['producciones'] or 0,
        'unidades_producidas': totales['unidades'] or CERO,
        'serie': _serie_desde_totales(unidades_por_bucket, claves, campo='unidades'),
        'top_productos': [
            {'producto': fila['producto__nombre_producto'], 'cantidad': fila['cantidad']} for fila in top_productos
        ],
    }
    if incluir_costo:
        resumen['costo_total'] = totales['costo'] or CERO
    return resumen


# --- Resumen facturación (`016`, "Actualización: Resumen facturación con datos")

# Vigentes ante el SAT: timbradas y las que esperan la aceptación de su
# cancelación. Mismo criterio que "Importe facturado" del listado de
# Facturación (`019`).
ESTADOS_FACTURA_VIGENTE = [Factura.ESTADO_TIMBRADA, Factura.ESTADO_PENDIENTE_CANCELACION]
# Orden fijo de la gráfica de barras; siempre los cinco, aunque estén en cero.
ESTADOS_FACTURA_GRAFICA = [
    (Factura.ESTADO_TIMBRADA, 'Timbrada'),
    (Factura.ESTADO_PENDIENTE, 'Pendiente'),
    (Factura.ESTADO_ERROR, 'Error'),
    (Factura.ESTADO_PENDIENTE_CANCELACION, 'Pendiente de cancelación'),
    (Factura.ESTADO_CANCELADA, 'Cancelada'),
]
ESTADOS_FACTURA_REQUIEREN_ATENCION = [Factura.ESTADO_ERROR, Factura.ESTADO_PENDIENTE_CANCELACION]
LIMITE_REQUIERE_ATENCION = 5


def _pagado_con_complementos():
    """Subconsulta: suma de los complementos de pago **timbrados** de la
    factura (los que fallaron no cuentan), mismo cálculo que el detalle de
    factura de `019`."""
    pagado = (
        ComplementoPago.objects.filter(factura=OuterRef('pk'), estado=ComplementoPago.ESTADO_TIMBRADO)
        .values('factura')
        .annotate(total=Sum('monto_pagado'))
        .values('total')
    )
    return Coalesce(Subquery(pagado, output_field=DecimalField(max_digits=12, decimal_places=2)), Value(CERO))


def _facturas_vigentes(rango: Rango, usuario):
    return _facturas(usuario).filter(estado__in=ESTADOS_FACTURA_VIGENTE, **_en_rango(rango, 'fecha_timbrado'))


def calcular_resumen_facturacion(rango: Rango, usuario=None) -> dict:
    """Resumen de la sección 'Resumen facturación' del Dashboard. Una factura
    pertenece al periodo por su fecha de timbrado (fecha fiscal del CFDI);
    las no timbradas usan su fecha de creación, solo para el conteo por
    estado. El importe de una factura es el total de su venta.
    """

    claves = _generar_claves(rango)
    vigentes = _facturas_vigentes(rango, usuario)
    anterior = rango_anterior(rango)

    facturado_total = vigentes.aggregate(total=Sum('venta__total'))['total'] or CERO
    facturas_emitidas = vigentes.count()
    facturado_anterior = (
        _facturas_vigentes(anterior, usuario).aggregate(total=Sum('venta__total'))['total'] or CERO
    )

    ppd = vigentes.filter(metodo_pago=Factura.METODO_PPD).annotate(pagado=_pagado_con_complementos())
    por_cobrar_ppd = sum(
        (max(total - pagado, CERO) for total, pagado in ppd.values_list('venta__total', 'pagado')), CERO,
    )

    # % del importe de las ventas del periodo (las que cuentan) que tiene
    # una factura vigente, sin importar cuándo se timbró.
    ventas = _ventas_que_cuentan(rango, usuario)
    importe_ventas = ventas.aggregate(total=Sum('total'))['total'] or CERO
    importe_facturado = (
        ventas.filter(facturas__estado__in=ESTADOS_FACTURA_VIGENTE).distinct().aggregate(total=Sum('total'))['total']
        or CERO
    )
    porcentaje_facturado = (
        (importe_facturado * CIEN / importe_ventas).quantize(Decimal('0.1')) if importe_ventas else None
    )

    pares = list(vigentes.values_list('fecha_timbrado', 'venta__total', 'metodo_pago'))
    pue = _agrupar_por_bucket(((f, m) for f, m, metodo in pares if metodo == Factura.METODO_PUE), rango.granularidad)
    ppd_bucket = _agrupar_por_bucket(
        ((f, m) for f, m, metodo in pares if metodo == Factura.METODO_PPD), rango.granularidad,
    )
    serie = [
        {
            'fecha': clave.isoformat(),
            'total': pue.get(clave, CERO) + ppd_bucket.get(clave, CERO),
            'pue': pue.get(clave, CERO),
            'ppd': ppd_bucket.get(clave, CERO),
        }
        for clave in claves
    ]

    # Fecha efectiva para contar: timbrado si existe, si no, creación.
    del_periodo_por_timbrado = _facturas(usuario).filter(**_en_rango(rango, 'fecha_timbrado'))
    del_periodo_sin_timbrar = _facturas(usuario).filter(
        fecha_timbrado__isnull=True, **_en_rango(rango, 'fecha_creacion'),
    )
    conteos = {}
    for consulta in (del_periodo_por_timbrado, del_periodo_sin_timbrar):
        for fila in consulta.values('estado').annotate(cantidad=Count('id')):
            conteos[fila['estado']] = conteos.get(fila['estado'], 0) + fila['cantidad']
    conteo_estado = [
        {'estado': estado, 'tipo': etiqueta, 'cantidad': conteos.get(estado, 0)}
        for estado, etiqueta in ESTADOS_FACTURA_GRAFICA
    ]

    # Pendientes accionables: no dependen del periodo.
    requiere_atencion = [
        {
            'id': factura.id,
            'serie': factura.serie,
            'folio_interno': factura.folio_interno,
            'cliente': factura.venta.cliente.nombre_cliente if factura.venta.cliente else 'Sin cliente',
            'total': factura.venta.total,
            'estado': factura.estado,
            'fecha': factura.fecha_creacion,
        }
        for factura in _facturas(usuario).filter(estado__in=ESTADOS_FACTURA_REQUIEREN_ATENCION)
        .select_related('venta__cliente')
        .order_by('-fecha_creacion')[:LIMITE_REQUIERE_ATENCION]
    ]

    return {
        'periodo': rango.periodo,
        'granularidad': rango.granularidad,
        'facturado_total': facturado_total,
        'facturas_emitidas': facturas_emitidas,
        'por_cobrar_ppd': por_cobrar_ppd,
        'porcentaje_facturado': porcentaje_facturado,
        'serie': serie,
        'conteo_estado': conteo_estado,
        'requiere_atencion': requiere_atencion,
        'periodo_anterior': _fechas_del_rango(anterior),
        'anterior': {'facturado_total': facturado_anterior},
        'variacion': {'facturado_total': _variacion(facturado_total, facturado_anterior)},
    }
