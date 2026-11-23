"""`011`, "Actualización — ajuste de inventario, filtros y traslado…"."""

from decimal import Decimal

import pytest
from django.core import mail
from rest_framework.test import APIClient

from apps.catalogo.models import Categoria, MateriaPrima, Producto
from apps.inventario.models import (
    InventarioSucursalMateriaPrima,
    InventarioSucursalProducto,
    MovimientoInventario,
)
from apps.sucursales.models import Sucursal
from apps.usuarios.models import Usuario

URL = '/api/inventario/ajustes/'


def _api(usuario):
    client = APIClient()
    client.force_authenticate(user=usuario)
    return client


@pytest.fixture
def admin(db):
    return Usuario.objects.create_user(
        username='admin1', email='admin1@flebosil.test', password='clave-segura-123', rol_usuario='admin',
    )


@pytest.fixture
def operador(db):
    return Usuario.objects.create_user(username='op1', email='op1@flebosil.test', password='clave-segura-123')


@pytest.fixture
def sucursal(db):
    return Sucursal.objects.create(nombre_sucursal='Matriz')


@pytest.fixture
def categoria(db):
    return Categoria.objects.create(nombre_categoria='General', tipo=Categoria.TIPO_AMBOS)


@pytest.fixture
def producto(categoria):
    return Producto.objects.create(
        nombre_producto='Medias', sku='SKU-AJ', unidad_medida='par', categoria=categoria, precio_venta=Decimal('250.00'),
    )


@pytest.fixture
def inventario(sucursal, producto):
    return InventarioSucursalProducto.objects.create(
        sucursal=sucursal, producto=producto, stock_actual=Decimal('10.00'), stock_minimo=Decimal('5.00'),
    )


def _ajuste(producto, sucursal, **extra):
    return {'tipo': 'producto', 'sucursal': sucursal.id, 'item_id': producto.id, **extra}


def test_salida_por_diferencia_con_observacion(admin, producto, sucursal, inventario):
    response = _api(admin).post(URL, _ajuste(
        producto, sucursal, stock_actual='8.00', stock_actual_visto='10.00', motivo_ajuste='merma', nota='Caja golpeada',
    ), format='json')

    assert response.status_code == 200, response.data
    assert response.data['stock_actual'] == '8.00'
    inventario.refresh_from_db()
    assert inventario.stock_actual == Decimal('8.00')
    movimiento = MovimientoInventario.objects.get()
    assert movimiento.tipo_movimiento == MovimientoInventario.SALIDA
    assert movimiento.motivo == MovimientoInventario.MOTIVO_AJUSTE
    assert movimiento.cantidad == Decimal('2.00')
    assert movimiento.stock_resultante == Decimal('8.00')
    assert movimiento.observacion == 'Merma o daño: Caja golpeada'
    assert movimiento.usuario == admin


def test_entrada_por_diferencia_sin_nota(admin, producto, sucursal, inventario):
    _api(admin).post(URL, _ajuste(
        producto, sucursal, stock_actual='13.50', stock_actual_visto='10.00', motivo_ajuste='conteo_fisico',
    ), format='json')

    movimiento = MovimientoInventario.objects.get()
    assert movimiento.tipo_movimiento == MovimientoInventario.ENTRADA
    assert movimiento.cantidad == Decimal('3.50')
    assert movimiento.observacion == 'Conteo físico'


def test_solo_el_minimo_no_genera_movimiento(admin, producto, sucursal, inventario):
    response = _api(admin).post(URL, _ajuste(producto, sucursal, stock_minimo='12'), format='json')

    assert response.status_code == 200
    assert response.data['stock_bajo'] is True
    inventario.refresh_from_db()
    assert inventario.stock_minimo == Decimal(12)
    assert inventario.stock_actual == Decimal('10.00')
    assert not MovimientoInventario.objects.exists()


def test_stock_y_minimo_juntos(admin, producto, sucursal, inventario):
    _api(admin).post(URL, _ajuste(
        producto, sucursal, stock_actual='4.00', stock_actual_visto='10.00', motivo_ajuste='caducidad', stock_minimo='6',
    ), format='json')

    inventario.refresh_from_db()
    assert (inventario.stock_actual, inventario.stock_minimo) == (Decimal('4.00'), Decimal(6))
    assert MovimientoInventario.objects.count() == 1


def test_mismo_stock_no_genera_movimiento(admin, producto, sucursal, inventario):
    response = _api(admin).post(URL, _ajuste(
        producto, sucursal, stock_actual='10.00', stock_actual_visto='10.00', motivo_ajuste='conteo_fisico',
    ), format='json')
    assert response.status_code == 200
    assert not MovimientoInventario.objects.exists()


@pytest.mark.parametrize(('extra', 'campo'), [
    ({'stock_actual': '8.00', 'stock_actual_visto': '10.00'}, 'motivo_ajuste'),
    ({'stock_actual': '8.00', 'stock_actual_visto': '10.00', 'motivo_ajuste': 'otro', 'nota': '  '}, 'nota'),
    ({'stock_actual': '-1.00', 'stock_actual_visto': '10.00', 'motivo_ajuste': 'merma'}, 'stock_actual'),
    ({'stock_actual': '8.00', 'motivo_ajuste': 'merma'}, 'stock_actual_visto'),
    ({'stock_minimo': '-2'}, 'stock_minimo'),
    ({'stock_minimo': '2.5'}, 'stock_minimo'),
    ({}, 'detail'),
])
def test_validaciones(admin, producto, sucursal, inventario, extra, campo):
    response = _api(admin).post(URL, _ajuste(producto, sucursal, **extra), format='json')

    assert response.status_code == 400
    assert campo in response.data
    inventario.refresh_from_db()
    assert inventario.stock_actual == Decimal('10.00')


def test_rechaza_si_el_stock_cambio_mientras_se_ajustaba(admin, producto, sucursal, inventario):
    response = _api(admin).post(URL, _ajuste(
        producto, sucursal, stock_actual='8.00', stock_actual_visto='12.00', motivo_ajuste='conteo_fisico',
        stock_minimo='7',
    ), format='json')

    assert response.status_code == 400
    assert 'cambió a 10.00' in str(response.data['detail'])
    inventario.refresh_from_db()
    assert (inventario.stock_actual, inventario.stock_minimo) == (Decimal('10.00'), Decimal('5.00'))
    assert not MovimientoInventario.objects.exists()


def test_el_operador_tambien_puede_ajustar(operador, producto, sucursal, inventario):
    response = _api(operador).post(URL, _ajuste(
        producto, sucursal, stock_actual='7.00', stock_actual_visto='10.00', motivo_ajuste='conteo_fisico',
        stock_minimo='3',
    ), format='json')

    assert response.status_code == 200, response.data
    inventario.refresh_from_db()
    assert (inventario.stock_actual, inventario.stock_minimo) == (Decimal('7.00'), Decimal(3))
    assert MovimientoInventario.objects.get().usuario == operador


def test_sin_sesion_no_hay_ajuste(db, producto, sucursal, inventario):
    assert APIClient().post(URL, _ajuste(producto, sucursal, stock_minimo='1'), format='json').status_code == 401


def test_item_sin_registro_en_la_sucursal(admin, categoria, sucursal):
    materia = MateriaPrima.objects.create(nombre_item='Tela', categoria=categoria, unidad_medida='m')

    response = _api(admin).post(URL, {
        'tipo': 'materia_prima', 'sucursal': sucursal.id, 'item_id': materia.id,
        'stock_actual': '2.50', 'stock_actual_visto': '0', 'motivo_ajuste': 'correccion',
    }, format='json')

    assert response.status_code == 200
    assert InventarioSucursalMateriaPrima.objects.get(materia_prima=materia).stock_actual == Decimal('2.50')


def test_item_inactivo(admin, producto, sucursal, inventario):
    Producto.objects.filter(pk=producto.pk).update(activo=False)
    response = _api(admin).post(URL, _ajuste(producto, sucursal, stock_minimo='1'), format='json')
    assert response.status_code == 400
    assert 'item_id' in response.data


def test_el_historial_muestra_la_observacion(admin, producto, sucursal, inventario):
    _api(admin).post(URL, _ajuste(
        producto, sucursal, stock_actual='9.00', stock_actual_visto='10.00', motivo_ajuste='merma',
    ), format='json')

    datos = _api(admin).get('/api/inventario/movimientos/').data
    filas = datos['results'] if isinstance(datos, dict) else datos
    assert filas[0]['observacion'] == 'Merma o daño'


def test_un_ajuste_a_cero_envia_el_aviso_inmediato(admin, producto, sucursal, inventario, django_capture_on_commit_callbacks):
    with django_capture_on_commit_callbacks(execute=True):
        _api(admin).post(URL, _ajuste(
            producto, sucursal, stock_actual='0', stock_actual_visto='10.00', motivo_ajuste='merma',
        ), format='json')

    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject.startswith('Agotado: Medias')


# --- Historial: el operador solo ve sus propios movimientos ---------------------


def _movimiento(sucursal, producto, usuario, cantidad):
    return MovimientoInventario.objects.create(
        sucursal=sucursal, tipo_item='producto', item_id=producto.id, tipo_movimiento=MovimientoInventario.ENTRADA,
        cantidad=Decimal(cantidad), motivo=MovimientoInventario.MOTIVO_COMPRA, stock_resultante=Decimal(cantidad),
        usuario=usuario,
    )


def _filas(respuesta):
    datos = respuesta.data
    return datos['results'] if isinstance(datos, dict) else datos


def test_el_operador_solo_ve_sus_movimientos(admin, operador, producto, sucursal):
    otro = Usuario.objects.create_user(username='op2', email='op2@flebosil.test', password='clave-segura-123')
    propio = _movimiento(sucursal, producto, operador, '1')
    _movimiento(sucursal, producto, otro, '2')
    _movimiento(sucursal, producto, admin, '3')

    filas = _filas(_api(operador).get('/api/inventario/movimientos/'))
    assert [fila['id'] for fila in filas] == [propio.id]

    # También con filtros, y sin poder abrir el detalle de un movimiento ajeno.
    assert len(_filas(_api(operador).get('/api/inventario/movimientos/', {'sucursal': sucursal.id}))) == 1
    ajeno = MovimientoInventario.objects.exclude(usuario=operador).first()
    assert _api(operador).get(f'/api/inventario/movimientos/{ajeno.id}/').status_code == 404


def test_el_admin_ve_todos_los_movimientos(admin, operador, producto, sucursal):
    _movimiento(sucursal, producto, operador, '1')
    _movimiento(sucursal, producto, admin, '3')

    assert len(_filas(_api(admin).get('/api/inventario/movimientos/'))) == 2
