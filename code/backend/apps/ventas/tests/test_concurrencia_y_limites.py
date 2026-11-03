"""Peticiones simultáneas sobre la misma venta (ej. doble clic), montos que
no caben en sus columnas y errores que siempre deben responder JSON."""

import threading
from decimal import Decimal

import pytest
from django.db import DataError, connection
from rest_framework.test import APIClient

from apps.caja.models import MovimientoCaja
from apps.catalogo.models import Categoria, Producto
from apps.inventario.models import InventarioSucursalProducto, MovimientoInventario
from apps.sucursales.models import Sucursal
from apps.usuarios.models import Usuario

PETICIONES_SIMULTANEAS = 6


def _cliente_api(usuario):
    client = APIClient(raise_request_exception=False)
    client.force_authenticate(user=usuario)
    return client


@pytest.fixture
def datos(db):
    admin = Usuario.objects.create_user(
        username='admin1', email='admin1@flebosil.test', password='clave-segura-123', rol_usuario='admin',
    )
    sucursal = Sucursal.objects.create(nombre_sucursal='Matriz')
    categoria = Categoria.objects.create(nombre_categoria='General', tipo=Categoria.TIPO_PRODUCTO)
    producto = Producto.objects.create(
        nombre_producto='Suero fisiológico', sku='SKU-1', unidad_medida='pza',
        categoria=categoria, precio_venta='45.00',
    )
    InventarioSucursalProducto.objects.create(sucursal=sucursal, producto=producto, stock_actual=Decimal(100))
    return {'admin': admin, 'sucursal': sucursal, 'producto': producto}


def _crear_venta(datos, cantidad='1', **extra):
    payload = {
        'sucursal': datos['sucursal'].id,
        'detalles': [{'producto': datos['producto'].id, 'cantidad': cantidad}],
    }
    payload.update(extra)
    return _cliente_api(datos['admin']).post('/api/ventas/', payload, format='json')


def _stock(datos):
    return InventarioSucursalProducto.objects.get(sucursal=datos['sucursal'], producto=datos['producto']).stock_actual


def _en_simultaneo(usuario, url):
    """Lanza la misma petición POST desde varios hilos a la vez y devuelve
    los códigos de respuesta, ordenados."""
    barrera = threading.Barrier(PETICIONES_SIMULTANEAS)
    codigos = []

    def peticion():
        try:
            client = _cliente_api(usuario)
            barrera.wait()
            codigos.append(client.post(url).status_code)
        finally:
            connection.close()

    hilos = [threading.Thread(target=peticion) for _ in range(PETICIONES_SIMULTANEAS)]
    for hilo in hilos:
        hilo.start()
    for hilo in hilos:
        hilo.join()
    return sorted(codigos)


@pytest.mark.django_db(transaction=True)
def test_entregar_en_simultaneo_retira_el_envio_una_sola_vez(catalogo_de_cuentas, datos):
    venta_id = _crear_venta(datos, gasto_envio='20.00', fecha_entrega='2026-12-01').data['id']

    codigos = _en_simultaneo(datos['admin'], f'/api/ventas/{venta_id}/entregar/')

    assert codigos == [200] + [400] * (PETICIONES_SIMULTANEAS - 1)
    retiros = MovimientoCaja.objects.filter(referencia_id=venta_id, tipo_movimiento=MovimientoCaja.RETIRO)
    assert retiros.count() == 1


@pytest.mark.django_db(transaction=True)
def test_cancelar_en_simultaneo_revierte_una_sola_vez(catalogo_de_cuentas, datos):
    venta_id = _crear_venta(datos, cantidad='4').data['id']
    assert _stock(datos) == Decimal(96)

    codigos = _en_simultaneo(datos['admin'], f'/api/ventas/{venta_id}/cancelar/')

    assert codigos == [200] + [400] * (PETICIONES_SIMULTANEAS - 1)
    assert _stock(datos) == Decimal(100)
    reversos = MovimientoInventario.objects.filter(
        referencia_id=venta_id, tipo_movimiento=MovimientoInventario.ENTRADA,
    )
    assert reversos.count() == 1


@pytest.mark.django_db
def test_cantidad_enorme_responde_400_sin_guardar_nada(datos):
    respuesta = _crear_venta(datos, cantidad='9999999999')

    assert respuesta.status_code == 400
    assert 'excede el máximo' in respuesta.data['detalles'][0]
    assert _stock(datos) == Decimal(100)
    assert not MovimientoCaja.objects.exists()


@pytest.mark.django_db
def test_producto_desactivado_responde_mensaje_claro(datos):
    datos['producto'].activo = False
    datos['producto'].save()

    respuesta = _crear_venta(datos)

    assert respuesta.status_code == 400
    assert respuesta.data['detalles'][0]['producto'][0] == 'El producto no existe o está desactivado.'


@pytest.mark.django_db
def test_sucursal_desactivada_responde_mensaje_claro(datos):
    datos['sucursal'].activo = False
    datos['sucursal'].save()

    respuesta = _crear_venta(datos)

    assert respuesta.status_code == 400
    assert respuesta.data['sucursal'][0] == 'La sucursal no existe o está desactivada.'


@pytest.mark.django_db
def test_mensajes_de_validacion_estandar_en_espanol(datos):
    respuesta = _cliente_api(datos['admin']).post('/api/ventas/', {}, format='json')

    assert respuesta.status_code == 400
    assert respuesta.data['sucursal'][0] == 'Este campo es requerido.'


@pytest.mark.django_db
def test_error_inesperado_responde_json_500(datos, monkeypatch):
    def falla(venta):
        raise RuntimeError('fallo simulado')

    monkeypatch.setattr('apps.ventas.views.generar_asiento_venta', falla)

    respuesta = _crear_venta(datos)

    assert respuesta.status_code == 500
    assert respuesta['Content-Type'] == 'application/json'
    assert 'error interno' in respuesta.json()['detail']
    # La transacción se revirtió: el stock no se descontó.
    assert _stock(datos) == Decimal(100)


@pytest.mark.django_db
def test_valor_fuera_de_rango_en_base_de_datos_responde_json_400(datos, monkeypatch):
    def falla(venta):
        raise DataError('numeric field overflow')

    monkeypatch.setattr('apps.ventas.views.generar_asiento_venta', falla)

    respuesta = _crear_venta(datos)

    assert respuesta.status_code == 400
    assert 'excede el máximo' in respuesta.json()['detail']
