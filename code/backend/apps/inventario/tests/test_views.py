import pytest
from rest_framework.test import APIClient

from apps.catalogo.models import Categoria, MateriaPrima, Producto
from apps.inventario.models import (
    InventarioSucursalMateriaPrima,
    InventarioSucursalProducto,
)
from apps.sucursales.models import Sucursal
from apps.usuarios.models import Usuario


@pytest.fixture
def usuario(db):
    return Usuario.objects.create_user(
        username='operador1', email='operador1@flebosil.test', password='clave-segura-123'
    )


@pytest.fixture
def api_client(usuario):
    client = APIClient()
    client.force_authenticate(user=usuario)
    return client


@pytest.fixture
def sucursal(db):
    return Sucursal.objects.create(nombre_sucursal='Matriz')


@pytest.mark.django_db
def test_alertas_vacio_sin_stock_bajo(api_client, sucursal):
    categoria = Categoria.objects.create(nombre_categoria='General')
    producto = Producto.objects.create(
        nombre_producto='Suero fisiológico', sku='SKU-1', unidad_medida='pza',
        categoria=categoria, precio_unitario='10.00',
    )
    InventarioSucursalProducto.objects.create(
        sucursal=sucursal, producto=producto, stock_actual='50.00', stock_minimo='10.00',
    )

    response = api_client.get('/api/inventario/alertas/')

    assert response.status_code == 200
    assert response.data == []


@pytest.mark.django_db
def test_alertas_incluye_producto_y_materia_prima_bajo_minimo(api_client, sucursal):
    categoria = Categoria.objects.create(nombre_categoria='General')
    producto = Producto.objects.create(
        nombre_producto='Suero fisiológico', sku='SKU-2', unidad_medida='pza',
        categoria=categoria, precio_unitario='10.00',
    )
    materia_prima = MateriaPrima.objects.create(nombre_item='Cloruro de sodio', unidad_medida='kg')

    InventarioSucursalProducto.objects.create(
        sucursal=sucursal, producto=producto, stock_actual='2.00', stock_minimo='10.00',
    )
    InventarioSucursalMateriaPrima.objects.create(
        sucursal=sucursal, materia_prima=materia_prima, stock_actual='1.00', stock_minimo='5.00',
    )

    response = api_client.get('/api/inventario/alertas/')

    assert response.status_code == 200
    tipos = {alerta['tipo'] for alerta in response.data}
    nombres = {alerta['nombre'] for alerta in response.data}
    assert tipos == {'producto', 'materia_prima'}
    assert nombres == {'Suero fisiológico', 'Cloruro de sodio'}
    for alerta in response.data:
        assert alerta['sucursal'] == 'Matriz'


@pytest.mark.django_db
def test_alertas_requiere_autenticacion(sucursal):
    client = APIClient()
    response = client.get('/api/inventario/alertas/')
    assert response.status_code == 401
