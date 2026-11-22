"""`001`, "Actualización: centro de notificaciones y avisos por correo"."""

from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

import pytest
from django.core import mail
from django.core.management import call_command
from django.utils import timezone
from rest_framework.test import APIClient

from apps.catalogo.models import Categoria, MateriaPrima, Producto
from apps.compras.models import Compra
from apps.facturacion.models import ComplementoPago, Factura
from apps.facturacion.tests.test_views import (  # noqa: F401 — fixtures reutilizadas
    _crear_venta,
    _mock_pac,
    _payload_factura,
    cliente_con_fiscales,
    serie_folio,
)
from apps.inventario.models import (
    InventarioSucursalMateriaPrima,
    InventarioSucursalProducto,
)
from apps.notificaciones.correo import enviar_resumen_diario
from apps.rrhh.models import Empleado, SolicitudNomina
from apps.sucursales.models import Sucursal
from apps.terceros.models import Cliente, Proveedor
from apps.usuarios.models import Usuario
from apps.ventas.models import Venta

URL = '/api/notificaciones/'


def _usuario(nombre, rol='operador', **extra):
    return Usuario.objects.create_user(
        username=nombre, email=f'{nombre}@flebosil.test', password='clave-segura-123', rol_usuario=rol, **extra,
    )


def _api(usuario):
    client = APIClient()
    client.force_authenticate(user=usuario)
    return client


@pytest.fixture
def operador(db):
    return _usuario('operador1')


@pytest.fixture
def otro_operador(db):
    return _usuario('operador2')


@pytest.fixture
def admin(db):
    return _usuario('admin1', rol='admin')


@pytest.fixture
def sucursal(db):
    return Sucursal.objects.create(nombre_sucursal='Matriz')


@pytest.fixture
def categoria(db):
    return Categoria.objects.create(nombre_categoria='General', tipo=Categoria.TIPO_AMBOS)


@pytest.fixture
def producto(categoria):
    return Producto.objects.create(
        nombre_producto='Medias de compresión', sku='SKU-N1', unidad_medida='par',
        categoria=categoria, precio_venta=Decimal('250.00'),
    )


@pytest.fixture
def proveedor(db):
    return Proveedor.objects.create(nombre_proveedor='Distribuidora Médica')


@pytest.fixture
def cliente(db):
    return Cliente.objects.create(nombre_cliente='Clínica Norte')


def _venta(sucursal, usuario, entrega=None, estado=Venta.ESTADO_PENDIENTE, cliente=None, total='100.00'):
    return Venta.objects.create(
        sucursal=sucursal, usuario=usuario, cliente=cliente, total=Decimal(total), estado=estado,
        fecha_entrega=entrega,
    )


def _compra(sucursal, proveedor, usuario, entrega=None, estado=Compra.ESTADO_PENDIENTE):
    return Compra.objects.create(
        sucursal=sucursal, proveedor=proveedor, usuario=usuario, total=Decimal('50.00'), estado=estado,
        fecha_entrega=entrega,
    )


def _factura(venta, usuario, estado=Factura.ESTADO_TIMBRADA, metodo=Factura.METODO_PPD):
    return Factura.objects.create(
        venta=venta, usuario=usuario, uso_cfdi='G03', forma_pago='99', metodo_pago=metodo, estado=estado,
        fecha_timbrado=timezone.now() if estado != Factura.ESTADO_ERROR else None,
    )


def _seccion(datos, clave):
    return next((s for s in datos['secciones'] if s['clave'] == clave), None)


def _dias(n):
    return timezone.localdate() + timedelta(days=n)


# --- Desplegable y contador -------------------------------------------------


def test_sin_pendientes_no_hay_secciones_ni_contador(admin):
    datos = _api(admin).get(URL).data
    assert datos == {'contador': 0, 'secciones': []}


def test_requiere_sesion(db):
    assert APIClient().get(URL).status_code == 401


def test_stock_bajo_el_minimo(admin, operador, sucursal, producto, categoria):
    InventarioSucursalProducto.objects.create(sucursal=sucursal, producto=producto, stock_actual=2, stock_minimo=10)
    materia = MateriaPrima.objects.create(nombre_item='Tela', categoria=categoria, unidad_medida='m')
    InventarioSucursalMateriaPrima.objects.create(sucursal=sucursal, materia_prima=materia, stock_actual=0, stock_minimo=5)

    for usuario in (admin, operador):
        stock = _seccion(_api(usuario).get(URL).data, 'stock')
        assert stock['total'] == 2
        assert stock['requieren_accion'] == 2
        assert [e['titulo'] for e in stock['elementos']] == ['Tela', 'Medias de compresión']
        assert stock['elementos'][1]['detalle'] == 'Matriz · 2 de 10 mínimo'


def test_ventas_por_entregar_vencidas_primero_y_solo_vencidas_cuentan(admin, sucursal, cliente):
    sin_fecha = _venta(sucursal, admin)
    proxima = _venta(sucursal, admin, entrega=_dias(3), cliente=cliente)
    vencida = _venta(sucursal, admin, entrega=_dias(-2))
    _venta(sucursal, admin, estado=Venta.ESTADO_ENTREGADA, entrega=_dias(-5))

    datos = _api(admin).get(URL).data
    ventas = _seccion(datos, 'ventas')

    assert ventas['total'] == 3
    assert ventas['requieren_accion'] == 1
    assert [e['titulo'] for e in ventas['elementos']] == [f'Venta #{vencida.id}', f'Venta #{proxima.id}', f'Venta #{sin_fecha.id}']
    assert ventas['elementos'][0]['etiqueta'] == 'Vencida · hace 2 días'
    assert ventas['elementos'][0]['urgente'] is True
    assert ventas['elementos'][0]['ruta'] == f'/ventas/{vencida.id}'
    assert ventas['elementos'][1]['detalle'].startswith('Clínica Norte · Entrega ')
    assert ventas['elementos'][1]['etiqueta'] is None
    assert ventas['elementos'][2]['detalle'] == 'Sin cliente · Sin fecha de entrega'
    assert datos['contador'] == 1


def test_vencida_de_un_dia_en_singular(admin, sucursal):
    _venta(sucursal, admin, entrega=_dias(-1))
    assert _seccion(_api(admin).get(URL).data, 'ventas')['elementos'][0]['etiqueta'] == 'Vencida · hace 1 día'


def test_compras_por_recibir(admin, sucursal, proveedor):
    _compra(sucursal, proveedor, admin, entrega=_dias(-4))
    _compra(sucursal, proveedor, admin)
    _compra(sucursal, proveedor, admin, estado=Compra.ESTADO_RECIBIDA)

    compras = _seccion(_api(admin).get(URL).data, 'compras')
    assert compras['total'] == 2
    assert compras['requieren_accion'] == 1
    assert compras['elementos'][0]['detalle'].startswith('Distribuidora Médica · Entrega ')


def test_cada_seccion_muestra_hasta_cinco(admin, sucursal):
    for _ in range(7):
        _venta(sucursal, admin, entrega=_dias(-1))
    datos = _api(admin).get(URL).data
    ventas = _seccion(datos, 'ventas')
    assert ventas['total'] == 7
    assert len(ventas['elementos']) == 5
    assert datos['contador'] == 7


def test_facturas_por_atender(admin, sucursal):
    con_saldo = _factura(_venta(sucursal, admin, estado=Venta.ESTADO_ENTREGADA, total='1000.00'), admin)
    ComplementoPago.objects.create(factura=con_saldo, usuario=admin, monto_pagado='300.00', fecha_pago=timezone.localdate())
    ComplementoPago.objects.create(
        factura=con_saldo, usuario=admin, monto_pagado='500.00', fecha_pago=timezone.localdate(),
        estado=ComplementoPago.ESTADO_ERROR,
    )
    pagada = _factura(_venta(sucursal, admin, estado=Venta.ESTADO_ENTREGADA, total='200.00'), admin)
    ComplementoPago.objects.create(factura=pagada, usuario=admin, monto_pagado='200.00', fecha_pago=timezone.localdate())
    _factura(_venta(sucursal, admin, estado=Venta.ESTADO_ENTREGADA), admin, metodo=Factura.METODO_PUE)
    error = _factura(_venta(sucursal, admin, estado=Venta.ESTADO_ENTREGADA), admin, estado=Factura.ESTADO_ERROR)
    cancelando = _factura(
        _venta(sucursal, admin, estado=Venta.ESTADO_ENTREGADA, total='400.00'), admin,
        estado=Factura.ESTADO_PENDIENTE_CANCELACION,
    )

    datos = _api(admin).get(URL).data
    facturas = _seccion(datos, 'facturas')

    # Error y cancelación pendiente (requieren acción) + PPD con saldo; la
    # pagada y la PUE no aparecen; la PPD en cancelación no se repite.
    assert facturas['total'] == 3
    assert facturas['requieren_accion'] == 2
    etiquetas = {e['ruta']: e['etiqueta'] for e in facturas['elementos']}
    assert etiquetas == {
        f'/facturacion/{error.id}': 'Error de timbrado',
        f'/facturacion/{cancelando.id}': 'Cancelación pendiente',
        f'/facturacion/{con_saldo.id}': 'Por cobrar $700.00',
    }
    assert facturas['elementos'][0]['ruta'] == f'/facturacion/{error.id}'
    assert datos['contador'] == 2


def test_nominas_solo_para_el_admin(admin, operador):
    empleado = Empleado.objects.create(nombre_completo='Laura Gómez')
    SolicitudNomina.objects.create(
        empleado=empleado, periodo_inicio=_dias(-15), periodo_fin=_dias(-1), monto=Decimal('5000.00'),
    )

    datos_admin = _api(admin).get(URL).data
    nominas = _seccion(datos_admin, 'nominas')
    assert nominas['total'] == 1
    assert nominas['elementos'][0]['titulo'] == 'Laura Gómez'
    assert nominas['elementos'][0]['detalle'].endswith('· $5,000.00')
    assert nominas['elementos'][0]['ruta'] == '/rrhh?pestana=nominas'
    assert datos_admin['contador'] == 1

    datos_operador = _api(operador).get(URL).data
    assert _seccion(datos_operador, 'nominas') is None
    assert datos_operador['contador'] == 0


def test_el_operador_solo_ve_sus_ventas_compras_y_facturas(admin, operador, otro_operador, sucursal, proveedor):
    _venta(sucursal, operador, entrega=_dias(-1))
    _venta(sucursal, otro_operador, entrega=_dias(-1))
    _compra(sucursal, proveedor, otro_operador, entrega=_dias(-1))
    _factura(_venta(sucursal, otro_operador, estado=Venta.ESTADO_ENTREGADA), otro_operador, estado=Factura.ESTADO_ERROR)

    datos = _api(operador).get(URL).data
    assert _seccion(datos, 'ventas')['total'] == 1
    assert _seccion(datos, 'compras') is None
    assert _seccion(datos, 'facturas') is None
    assert datos['contador'] == 1

    datos_admin = _api(admin).get(URL).data
    assert _seccion(datos_admin, 'ventas')['total'] == 2
    assert datos_admin['contador'] == 4


# --- Preferencias de correo ---------------------------------------------------


def test_el_admin_cambia_sus_preferencias(admin):
    api = _api(admin)
    assert api.get('/api/usuarios/me/').data['recibe_resumen_diario'] is True

    response = api.patch('/api/usuarios/me/preferencias/', {'recibe_resumen_diario': False}, format='json')

    assert response.status_code == 200
    assert response.data == {'recibe_resumen_diario': False, 'recibe_alertas_criticas': True}
    admin.refresh_from_db()
    assert admin.recibe_resumen_diario is False
    assert admin.recibe_alertas_criticas is True


def test_el_operador_no_puede_cambiar_preferencias(operador):
    response = _api(operador).patch('/api/usuarios/me/preferencias/', {'recibe_alertas_criticas': False}, format='json')
    assert response.status_code == 403
    operador.refresh_from_db()
    assert operador.recibe_alertas_criticas is True


# --- Resumen diario -----------------------------------------------------------


def test_resumen_diario_a_los_admins_con_el_resumen_activo(admin, operador, sucursal):
    _usuario('admin2', rol='admin', recibe_resumen_diario=False)
    _usuario('admin3', rol='admin', is_active=False)
    _venta(sucursal, operador, entrega=_dias(-3))

    call_command('enviar_resumen_diario')

    assert [correo.to for correo in mail.outbox] == [['admin1@flebosil.test']]
    correo = mail.outbox[0]
    assert 'Resumen del día' in correo.subject
    assert '1 pendiente por atender' in correo.subject
    html = correo.alternatives[0][0]
    assert 'Ventas por entregar · 1' in html
    assert 'Vencida · hace 3 días' in html
    assert 'cid:logo_flebosil' in html
    assert '/informacion-usuario' in html
    assert 'Ventas por entregar (1)' in correo.body


def test_resumen_diario_no_se_envia_sin_pendientes(admin):
    assert enviar_resumen_diario() == 0
    assert mail.outbox == []


def test_resumen_diario_a_correos_de_prueba(admin, sucursal):
    _venta(sucursal, admin)
    assert enviar_resumen_diario(para=['prueba@flebosil.test']) == 1
    assert mail.outbox[0].to == ['prueba@flebosil.test']


def test_un_fallo_de_correo_no_detiene_el_resumen(admin, sucursal):
    _usuario('admin2', rol='admin')
    _venta(sucursal, admin)
    with patch('django.core.mail.EmailMultiAlternatives.send', side_effect=[OSError('smtp caído'), 1]):
        assert enviar_resumen_diario() == 1


# --- Avisos inmediatos --------------------------------------------------------


@pytest.fixture
def stock_justo(sucursal, producto):
    return InventarioSucursalProducto.objects.create(
        sucursal=sucursal, producto=producto, stock_actual=Decimal('2.00'), stock_minimo=Decimal('1.00'),
    )


def _vender(admin, sucursal, producto, cantidad):
    return _api(admin).post(
        '/api/ventas/', {'sucursal': sucursal.id, 'detalles': [{'producto': producto.id, 'cantidad': cantidad}]},
        format='json',
    )


def test_aviso_inmediato_cuando_el_stock_llega_a_cero(admin, sucursal, producto, stock_justo, django_capture_on_commit_callbacks):
    _usuario('admin2', rol='admin', recibe_alertas_criticas=False)

    with django_capture_on_commit_callbacks(execute=True):
        response = _vender(admin, sucursal, producto, '2.00')

    assert response.status_code == 201, response.data
    assert [correo.to for correo in mail.outbox] == [['admin1@flebosil.test']]
    assert mail.outbox[0].subject == 'Agotado: Medias de compresión en Matriz — FleboSil'


def test_sin_aviso_si_el_stock_no_llega_a_cero(admin, sucursal, producto, stock_justo, django_capture_on_commit_callbacks):
    with django_capture_on_commit_callbacks(execute=True):
        _vender(admin, sucursal, producto, '1.00')
    assert mail.outbox == []


def test_como_maximo_un_aviso_por_elemento_al_dia(admin, sucursal, producto, stock_justo, django_capture_on_commit_callbacks):
    with django_capture_on_commit_callbacks(execute=True):
        _vender(admin, sucursal, producto, '2.00')
    stock_justo.refresh_from_db()
    InventarioSucursalProducto.objects.filter(pk=stock_justo.pk).update(stock_actual=Decimal('1.00'))
    with django_capture_on_commit_callbacks(execute=True):
        _vender(admin, sucursal, producto, '1.00')

    assert len(mail.outbox) == 1


def test_un_fallo_de_correo_no_revierte_la_venta(admin, sucursal, producto, stock_justo, django_capture_on_commit_callbacks):
    with (
        patch('django.core.mail.EmailMultiAlternatives.send', side_effect=OSError('smtp caído')),
        django_capture_on_commit_callbacks(execute=True),
    ):
        response = _vender(admin, sucursal, producto, '2.00')

    assert response.status_code == 201
    assert Venta.objects.filter(id=response.data['id']).exists()
    stock_justo.refresh_from_db()
    assert stock_justo.stock_actual == 0


def test_aviso_inmediato_cuando_falla_el_timbrado(
    admin, sucursal, producto, stock_justo, cliente_con_fiscales, serie_folio, django_capture_on_commit_callbacks,  # noqa: F811
):
    api = _api(admin)
    venta = _crear_venta(api, sucursal, producto, cliente=cliente_con_fiscales, cantidad='1.00')
    parche, _ = _mock_pac(respuesta_timbrar={'exito': False, 'error': 'RFC del receptor no válido.'})

    with parche, django_capture_on_commit_callbacks(execute=True):
        response = api.post('/api/facturacion/', _payload_factura(venta), format='json')

    assert response.data['estado'] == 'error'
    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == f'Error de timbrado: Factura #{response.data["id"]} — FleboSil'
    assert 'RFC del receptor no válido.' in mail.outbox[0].body
