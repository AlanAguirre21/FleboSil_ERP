"""`016`, "Actualización: periodos ampliados, comparación y producción"."""

from datetime import datetime, time, timedelta
from decimal import Decimal

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from apps.catalogo.models import Categoria, Producto
from apps.produccion.models import Produccion
from apps.reportes.services import (
    GRANULARIDAD_SEMANA,
    PERIODO_ANIO,
    PERIODO_DIA,
    PERIODO_MES,
    PERIODO_PERSONALIZADO,
    PERIODO_SEMANA,
    rango_anterior,
    resolver_rango,
)
from apps.sucursales.models import Sucursal
from apps.usuarios.models import Usuario
from apps.ventas.models import DetalleVenta, Venta

ENDPOINTS = [
    '/api/reportes/resumen/',
    '/api/reportes/ventas/',
    '/api/reportes/compras/',
    '/api/reportes/productos-top/',
    '/api/reportes/clientes-top/',
    '/api/reportes/facturacion/',
    '/api/reportes/produccion/',
]


def _usuario(nombre, rol='operador'):
    return Usuario.objects.create_user(
        username=nombre, email=f'{nombre}@flebosil.test', password='clave-segura-123', rol_usuario=rol,
    )


def _api(usuario):
    client = APIClient()
    client.force_authenticate(user=usuario)
    return client


@pytest.fixture
def operador(db):
    return _usuario('operador1')


@pytest.fixture
def admin(db):
    return _usuario('admin1', rol='admin')


@pytest.fixture
def api_operador(operador):
    return _api(operador)


@pytest.fixture
def api_admin(admin):
    return _api(admin)


@pytest.fixture
def sucursal(db):
    return Sucursal.objects.create(nombre_sucursal='Matriz')


@pytest.fixture
def categoria(db):
    return Categoria.objects.create(nombre_categoria='General', tipo=Categoria.TIPO_AMBOS)


def _producto(categoria, nombre, sku):
    return Producto.objects.create(
        nombre_producto=nombre, sku=sku, unidad_medida='par', categoria=categoria, precio_venta=Decimal('10.00'),
    )


def _a_mediodia(dias_atras):
    dia = timezone.localdate() - timedelta(days=dias_atras)
    return timezone.make_aware(datetime.combine(dia, time(12)))


def _venta(sucursal, usuario, total, fecha=None):
    venta = Venta.objects.create(sucursal=sucursal, usuario=usuario, total=total)
    if fecha is not None:
        Venta.objects.filter(pk=venta.pk).update(fecha=fecha)
    return venta


def _rango_personalizado(desde_dias_atras, hasta_dias_atras):
    hoy = timezone.localdate()
    return {
        'periodo': 'personalizado',
        'desde': (hoy - timedelta(days=desde_dias_atras)).isoformat(),
        'hasta': (hoy - timedelta(days=hasta_dias_atras)).isoformat(),
    }


# --- Restricción del operador, ahora en el backend ---------------------------


@pytest.mark.parametrize('url', ENDPOINTS + ['/api/reportes/movimientos-caja/'])
@pytest.mark.parametrize('periodo', ['semana', 'mes', 'año', 'personalizado'])
def test_operador_solo_puede_consultar_dia(api_operador, url, periodo):
    response = api_operador.get(url, {'periodo': periodo})
    assert response.status_code == 403
    assert 'detail' in response.data


@pytest.mark.parametrize('url', ENDPOINTS)
def test_operador_no_puede_mandar_fechas_aunque_pida_dia(api_operador, url):
    hoy = timezone.localdate().isoformat()
    response = api_operador.get(url, {'periodo': 'dia', 'desde': hoy, 'hasta': hoy})
    assert response.status_code == 403


@pytest.mark.parametrize('url', ENDPOINTS)
def test_operador_consulta_dia_sin_problema(api_operador, url):
    assert api_operador.get(url, {'periodo': 'dia'}).status_code == 200
    assert api_operador.get(url).status_code == 200


def test_operador_con_periodo_inexistente_recibe_400(api_operador):
    response = api_operador.get('/api/reportes/resumen/', {'periodo': 'trimestre'})
    assert response.status_code == 400
    assert 'periodo' in response.data


# --- Validación del rango personalizado -------------------------------------


@pytest.mark.parametrize(
    ('parametros', 'campo'),
    [
        ({'periodo': 'personalizado'}, 'desde'),
        ({'periodo': 'personalizado', 'desde': '2026-01-01'}, 'hasta'),
        ({'periodo': 'personalizado', 'desde': 'ayer', 'hasta': '2026-01-01'}, 'desde'),
    ],
)
def test_rango_personalizado_incompleto_o_mal_formado(api_admin, parametros, campo):
    response = api_admin.get('/api/reportes/resumen/', parametros)
    assert response.status_code == 400
    assert campo in response.data


def test_desde_no_puede_ser_posterior_a_hasta(api_admin):
    response = api_admin.get('/api/reportes/resumen/', _rango_personalizado(1, 3))
    assert response.status_code == 400
    assert 'desde' in response.data


def test_hasta_no_puede_ser_futuro(api_admin):
    response = api_admin.get('/api/reportes/resumen/', _rango_personalizado(1, -1))
    assert response.status_code == 400
    assert 'hasta' in response.data


def test_rango_maximo_de_dos_anios(api_admin):
    assert api_admin.get('/api/reportes/resumen/', _rango_personalizado(730, 0)).status_code == 200
    response = api_admin.get('/api/reportes/resumen/', _rango_personalizado(731, 0))
    assert response.status_code == 400
    assert 'hasta' in response.data


def test_rango_personalizado_es_inclusivo_por_dias_completos(api_admin, sucursal, admin):
    hoy = timezone.localdate()
    dia = hoy - timedelta(days=5)
    zona = timezone.get_current_timezone()
    _venta(sucursal, admin, Decimal('10.00'), fecha=timezone.make_aware(datetime.combine(dia, time(0, 0)), zona))
    _venta(sucursal, admin, Decimal('20.00'), fecha=timezone.make_aware(datetime.combine(dia, time(23, 59, 59)), zona))
    _venta(sucursal, admin, Decimal('40.00'), fecha=timezone.make_aware(datetime.combine(dia - timedelta(days=1), time(23, 59)), zona))

    response = api_admin.get('/api/reportes/resumen/', _rango_personalizado(5, 5))

    assert response.data['ventas_total'] == '30.00'
    assert response.data['periodo'] == 'personalizado'


# --- Agrupación ---------------------------------------------------------------


@pytest.mark.parametrize(
    ('desde', 'hasta', 'granularidad'),
    [(1, 0, 'hora'), (2, 0, 'dia'), (91, 0, 'dia'), (92, 0, 'semana'), (365, 0, 'semana'), (366, 0, 'mes')],
)
def test_granularidad_segun_la_duracion_del_rango(api_admin, desde, hasta, granularidad):
    response = api_admin.get('/api/reportes/ventas/', _rango_personalizado(desde, hasta))
    assert response.data['granularidad'] == granularidad


def test_agrupacion_semanal_usa_lunes_y_suma_la_semana(api_admin, sucursal, admin):
    _venta(sucursal, admin, Decimal('100.00'), fecha=_a_mediodia(20))
    _venta(sucursal, admin, Decimal('50.00'), fecha=_a_mediodia(20))

    response = api_admin.get('/api/reportes/ventas/', _rango_personalizado(120, 0))

    assert response.data['granularidad'] == 'semana'
    fechas = [datetime.fromisoformat(p['fecha']) for p in response.data['con_envio']]
    assert all(fecha.weekday() == 0 and fecha.hour == 0 for fecha in fechas)
    con_monto = [p for p in response.data['con_envio'] if Decimal(p['monto']) != 0]
    assert len(con_monto) == 1
    assert con_monto[0]['monto'] == '150.00'


# --- Periodo anterior ----------------------------------------------------------


def _local(anio, mes, dia, hora=0, minuto=0):
    return datetime(anio, mes, dia, hora, minuto, tzinfo=timezone.get_current_timezone())


def test_periodo_anterior_de_dia_es_ayer_hasta_la_misma_hora():
    anterior = rango_anterior(resolver_rango(PERIODO_DIA, ahora=_local(2026, 3, 10, 15, 30)))
    assert anterior.inicio == _local(2026, 3, 9)
    assert anterior.fin == _local(2026, 3, 9, 15, 30)


def test_periodo_anterior_de_semana_es_el_mismo_tramo_de_la_semana_pasada():
    # Miércoles 11 de marzo de 2026: la semana empieza el lunes 9.
    anterior = rango_anterior(resolver_rango(PERIODO_SEMANA, ahora=_local(2026, 3, 11, 9)))
    assert anterior.inicio == _local(2026, 3, 2)
    assert anterior.fin == _local(2026, 3, 4, 9)


def test_periodo_anterior_de_mes_se_limita_al_ultimo_dia_del_mes_corto():
    anterior = rango_anterior(resolver_rango(PERIODO_MES, ahora=_local(2026, 3, 31, 18)))
    assert anterior.inicio == _local(2026, 2, 1)
    assert anterior.fin == _local(2026, 2, 28, 18)


def test_periodo_anterior_de_anio_con_29_de_febrero():
    anterior = rango_anterior(resolver_rango(PERIODO_ANIO, ahora=_local(2028, 2, 29, 12)))
    assert anterior.inicio == _local(2027, 1, 1)
    assert anterior.fin == _local(2027, 2, 28, 12)


def test_periodo_anterior_de_un_rango_personalizado_es_la_ventana_previa_de_igual_duracion():
    from datetime import date

    rango = resolver_rango(PERIODO_PERSONALIZADO, date(2026, 3, 1), date(2026, 3, 15), ahora=_local(2026, 6, 1))
    anterior = rango_anterior(rango)
    assert anterior.inicio == _local(2026, 2, 14)
    assert anterior.fin.date() == date(2026, 2, 28)
    assert anterior.fin < rango.inicio


def test_rango_personalizado_que_termina_hoy_llega_hasta_ahora():
    ahora = _local(2026, 3, 15, 10)
    rango = resolver_rango(PERIODO_PERSONALIZADO, ahora.date(), ahora.date(), ahora=ahora)
    assert rango.fin == ahora


# --- Comparación en las respuestas --------------------------------------------


def test_resumen_trae_variacion_contra_el_periodo_anterior(api_admin, sucursal, admin):
    # Rango: hace 3 y 2 días; anterior: hace 5 y 4 días.
    _venta(sucursal, admin, Decimal('150.00'), fecha=_a_mediodia(2))
    _venta(sucursal, admin, Decimal('100.00'), fecha=_a_mediodia(4))

    response = api_admin.get('/api/reportes/resumen/', _rango_personalizado(3, 2))

    assert response.data['ventas_total'] == '150.00'
    assert response.data['anterior']['ventas_total'] == '100.00'
    assert response.data['variacion']['ventas_total'] == '50.0'
    assert response.data['anterior']['ganancia'] == '100.00'
    assert response.data['variacion']['ganancia'] == '50.0'


def test_variacion_es_null_si_el_periodo_anterior_es_cero(api_admin, sucursal, admin):
    _venta(sucursal, admin, Decimal('150.00'), fecha=_a_mediodia(2))

    response = api_admin.get('/api/reportes/resumen/', _rango_personalizado(3, 2))

    assert response.data['anterior']['ventas_total'] == '0.00'
    assert response.data['variacion']['ventas_total'] is None
    assert response.data['variacion']['compras_total'] is None


def test_operador_recibe_su_comparacion_sin_la_ganancia(api_operador, sucursal, operador):
    _venta(sucursal, operador, Decimal('80.00'))

    response = api_operador.get('/api/reportes/resumen/', {'periodo': 'dia'})

    assert set(response.data['anterior']) == {'ventas_total', 'compras_total'}
    assert set(response.data['variacion']) == {'ventas_total', 'compras_total'}
    assert 'ganancia' not in response.data


def test_facturacion_trae_la_variacion_de_lo_facturado(api_admin):
    response = api_admin.get('/api/reportes/facturacion/', {'periodo': 'mes'})
    assert response.data['anterior'] == {'facturado_total': '0.00'}
    assert response.data['variacion'] == {'facturado_total': None}
    assert 'granularidad' in response.data


# --- Número de ventas y ticket promedio ---------------------------------------


def test_numero_de_ventas_y_ticket_promedio(api_admin, sucursal, admin):
    _venta(sucursal, admin, Decimal('100.00'), fecha=_a_mediodia(2))
    _venta(sucursal, admin, Decimal('50.00'), fecha=_a_mediodia(2))
    cancelada = _venta(sucursal, admin, Decimal('999.00'), fecha=_a_mediodia(2))
    Venta.objects.filter(pk=cancelada.pk).update(estado=Venta.ESTADO_CANCELADA)
    _venta(sucursal, admin, Decimal('60.00'), fecha=_a_mediodia(4))

    response = api_admin.get('/api/reportes/ventas/', _rango_personalizado(3, 2))

    assert response.data['numero_ventas'] == 2
    assert response.data['ticket_promedio'] == '75.00'
    assert response.data['anterior'] == {'numero_ventas': 1, 'ticket_promedio': '60.00'}
    assert response.data['variacion'] == {'numero_ventas': '100.0', 'ticket_promedio': '25.0'}


def test_ticket_promedio_es_null_sin_ventas(api_operador):
    response = api_operador.get('/api/reportes/ventas/', {'periodo': 'dia'})
    assert response.data['numero_ventas'] == 0
    assert response.data['ticket_promedio'] is None
    assert response.data['variacion']['ticket_promedio'] is None


# --- Top de productos por importe ---------------------------------------------


def _detalle(venta, producto, cantidad, subtotal):
    DetalleVenta.objects.create(
        venta=venta, producto=producto, cantidad=Decimal(cantidad),
        precio_unitario=Decimal(subtotal) / Decimal(cantidad), subtotal=Decimal(subtotal),
    )


def test_top_de_productos_por_importe_para_el_admin(api_admin, sucursal, admin, categoria):
    barato = _producto(categoria, 'Gasa', 'SKU-1')
    caro = _producto(categoria, 'Medias', 'SKU-2')
    venta = _venta(sucursal, admin, Decimal('550.00'))
    _detalle(venta, barato, '50', '50.00')
    _detalle(venta, caro, '2', '500.00')

    por_cantidad = api_admin.get('/api/reportes/productos-top/', {'periodo': 'mes'}).data
    por_importe = api_admin.get('/api/reportes/productos-top/', {'periodo': 'mes', 'por': 'importe'}).data
    menos_por_importe = api_admin.get(
        '/api/reportes/productos-top/', {'periodo': 'mes', 'por': 'importe', 'orden': 'menos'},
    ).data

    assert [fila['producto'] for fila in por_cantidad] == ['Gasa', 'Medias']
    assert por_importe == [{'producto': 'Medias', 'importe': '500.00'}, {'producto': 'Gasa', 'importe': '50.00'}]
    assert [fila['producto'] for fila in menos_por_importe] == ['Gasa', 'Medias']


def test_top_de_productos_por_importe_es_solo_de_admin(api_operador):
    response = api_operador.get('/api/reportes/productos-top/', {'periodo': 'dia', 'por': 'importe'})
    assert response.status_code == 403


def test_top_de_productos_con_criterio_invalido(api_admin):
    response = api_admin.get('/api/reportes/productos-top/', {'periodo': 'mes', 'por': 'precio'})
    assert response.status_code == 400
    assert 'por' in response.data


# --- Resumen de producción ----------------------------------------------------


def _produccion(producto, sucursal, usuario, cantidad, costo, fecha=None):
    produccion = Produccion.objects.create(
        producto=producto, sucursal=sucursal, usuario=usuario,
        cantidad_producida=Decimal(cantidad), costo_total=Decimal(costo),
    )
    if fecha is not None:
        Produccion.objects.filter(pk=produccion.pk).update(fecha=fecha)
    return produccion


@pytest.fixture
def producciones(sucursal, categoria, admin, operador):
    medias = _producto(categoria, 'Medias', 'SKU-1')
    vendas = _producto(categoria, 'Vendas', 'SKU-2')
    _produccion(medias, sucursal, admin, '10', '200.00')
    _produccion(medias, sucursal, operador, '5', '100.00')
    _produccion(vendas, sucursal, admin, '3', '30.00')
    _produccion(vendas, sucursal, admin, '100', '999.00', fecha=_a_mediodia(400))  # fuera del periodo


def test_resumen_de_produccion_del_admin(api_admin, producciones):
    response = api_admin.get('/api/reportes/produccion/', {'periodo': 'dia'})

    assert response.status_code == 200
    assert response.data['producciones'] == 3
    assert response.data['unidades_producidas'] == '18.00'
    assert response.data['costo_total'] == '330.00'
    assert response.data['granularidad'] == 'hora'
    assert sum(Decimal(p['unidades']) for p in response.data['serie']) == Decimal(18)
    assert response.data['top_productos'] == [
        {'producto': 'Medias', 'cantidad': '15.00'},
        {'producto': 'Vendas', 'cantidad': '3.00'},
    ]


def test_resumen_de_produccion_del_operador_es_de_toda_la_empresa_sin_costo(api_operador, producciones):
    response = api_operador.get('/api/reportes/produccion/', {'periodo': 'dia'})

    assert response.status_code == 200
    assert response.data['producciones'] == 3
    assert response.data['unidades_producidas'] == '18.00'
    assert 'costo_total' not in response.data


def test_resumen_de_produccion_sin_producciones(api_admin):
    response = api_admin.get('/api/reportes/produccion/', {'periodo': 'mes'})

    assert response.data['producciones'] == 0
    assert response.data['unidades_producidas'] == '0.00'
    assert response.data['costo_total'] == '0.00'
    assert response.data['top_productos'] == []


def test_resumen_de_produccion_requiere_sesion(db):
    assert APIClient().get('/api/reportes/produccion/').status_code == 401


def test_rango_de_casi_seis_meses_agrupa_por_semana():
    from datetime import date

    rango = resolver_rango(PERIODO_PERSONALIZADO, date(2026, 1, 7), date(2026, 6, 30), ahora=_local(2026, 7, 1))
    assert rango.granularidad == GRANULARIDAD_SEMANA


@pytest.mark.parametrize('periodo', ['ultimos_7', 'ultimos_30'])
def test_las_ventanas_moviles_no_son_un_periodo_valido(api_admin, periodo):
    response = api_admin.get('/api/reportes/resumen/', {'periodo': periodo})
    assert response.status_code == 400


@pytest.mark.parametrize('url', ['/api/reportes/resumen/', '/api/reportes/ventas/', '/api/reportes/facturacion/'])
def test_las_comparaciones_traen_las_fechas_del_periodo_anterior(api_admin, url):
    response = api_admin.get(url, _rango_personalizado(3, 2))

    hoy = timezone.localdate()
    inicio = datetime.fromisoformat(response.data['periodo_anterior']['inicio'])
    fin = datetime.fromisoformat(response.data['periodo_anterior']['fin'])
    assert inicio.date() == hoy - timedelta(days=5)
    assert (inicio.hour, inicio.minute) == (0, 0)
    assert fin.date() == hoy - timedelta(days=4)


def test_el_operador_recibe_las_fechas_de_su_dia_anterior(api_operador):
    response = api_operador.get('/api/reportes/resumen/', {'periodo': 'dia'})

    inicio = datetime.fromisoformat(response.data['periodo_anterior']['inicio'])
    assert inicio.date() == timezone.localdate() - timedelta(days=1)
