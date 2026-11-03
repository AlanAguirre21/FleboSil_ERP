"""Peticiones simultáneas sobre la misma compra y montos que no caben en
sus columnas."""

import threading
from decimal import Decimal

import pytest
from django.db import connection, transaction
from rest_framework.test import APIClient

from apps.caja.models import MovimientoCaja
from apps.caja.services import registrar_movimiento_caja
from apps.catalogo.models import Categoria, Producto
from apps.compras.models import Compra
from apps.inventario.models import InventarioSucursalProducto
from apps.sucursales.models import Sucursal
from apps.terceros.models import Proveedor
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
    # Crear una compra retira su total de caja: se fondea antes. Dentro de
    # `atomic()` porque en las pruebas transaccionales no hay una abierta.
    with transaction.atomic():
        registrar_movimiento_caja(
            tipo_movimiento=MovimientoCaja.INGRESO, monto=Decimal('1000000.00'), motivo=MovimientoCaja.MOTIVO_MANUAL,
            referencia_id=None, usuario=admin, observacion='Fondeo inicial para tests',
        )
    categoria = Categoria.objects.create(nombre_categoria='General', tipo=Categoria.TIPO_PRODUCTO)
    return {
        'admin': admin,
        'sucursal': Sucursal.objects.create(nombre_sucursal='Matriz'),
        'proveedor': Proveedor.objects.create(nombre_proveedor='Distribuidora Médica'),
        'producto': Producto.objects.create(
            nombre_producto='Suero fisiológico', sku='SKU-1', unidad_medida='pza',
            categoria=categoria, precio_venta='45.00',
        ),
    }


def _crear_compra(datos, cantidad='10.00', costo_unitario='5.50'):
    payload = {
        'proveedor': datos['proveedor'].id, 'sucursal': datos['sucursal'].id,
        'detalles_producto': [{'producto': datos['producto'].id, 'cantidad': cantidad, 'costo_unitario': costo_unitario}],
        'detalles_materia_prima': [],
    }
    return _cliente_api(datos['admin']).post('/api/compras/', payload, format='json')


def _en_simultaneo(usuario, url):
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
def test_recibir_en_simultaneo_suma_el_stock_una_sola_vez(catalogo_de_cuentas, datos):
    compra_id = _crear_compra(datos).data['id']

    codigos = _en_simultaneo(datos['admin'], f'/api/compras/{compra_id}/recibir/')

    assert codigos == [200] + [400] * (PETICIONES_SIMULTANEAS - 1)
    inventario = InventarioSucursalProducto.objects.get(sucursal=datos['sucursal'], producto=datos['producto'])
    assert inventario.stock_actual == Decimal('10.00')


@pytest.mark.django_db
def test_total_enorme_responde_400_sin_guardar_nada(datos):
    respuesta = _crear_compra(datos, cantidad='9999999999.00', costo_unitario='5.50')

    assert respuesta.status_code == 400
    assert 'excede el máximo' in respuesta.data['non_field_errors'][0]
    assert not Compra.objects.exists()


@pytest.mark.django_db
def test_proveedor_desactivado_responde_mensaje_claro(datos):
    datos['proveedor'].activo = False
    datos['proveedor'].save()

    respuesta = _crear_compra(datos)

    assert respuesta.status_code == 400
    assert respuesta.data['proveedor'][0] == 'El proveedor no existe o está desactivado.'
