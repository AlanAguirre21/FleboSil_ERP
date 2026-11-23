"""Producción: el operador solo ve las producciones que registró; el admin,
todas (mismo criterio de propiedad que Ventas, Compras e Inventario)."""

from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from apps.catalogo.models import Categoria, Producto
from apps.produccion.models import Produccion
from apps.sucursales.models import Sucursal
from apps.usuarios.models import Usuario

URL = '/api/produccion/'


def _usuario(nombre, rol='operador'):
    return Usuario.objects.create_user(
        username=nombre, email=f'{nombre}@flebosil.test', password='clave-segura-123', rol_usuario=rol,
    )


def _api(usuario):
    client = APIClient()
    client.force_authenticate(user=usuario)
    return client


def _filas(respuesta):
    datos = respuesta.data
    return datos['results'] if isinstance(datos, dict) else datos


@pytest.fixture
def datos(db):
    sucursal = Sucursal.objects.create(nombre_sucursal='Matriz')
    categoria = Categoria.objects.create(nombre_categoria='General', tipo=Categoria.TIPO_AMBOS)
    producto = Producto.objects.create(
        nombre_producto='Medias', sku='SKU-P1', unidad_medida='par', categoria=categoria, precio_venta=Decimal(1),
    )
    ana, luis, admin = _usuario('ana'), _usuario('luis'), _usuario('admin1', rol='admin')

    def producir(usuario):
        return Produccion.objects.create(
            producto=producto, sucursal=sucursal, usuario=usuario, cantidad_producida=Decimal(2),
        )

    return {'ana': ana, 'admin': admin, 'propia': producir(ana), 'ajena': producir(luis), 'del_admin': producir(admin)}


def test_el_operador_solo_lista_sus_producciones(datos):
    assert [fila['id'] for fila in _filas(_api(datos['ana']).get(URL))] == [datos['propia'].id]


def test_una_produccion_ajena_responde_404(datos):
    assert _api(datos['ana']).get(f'{URL}{datos["ajena"].id}/').status_code == 404
    assert _api(datos['ana']).get(f'{URL}{datos["propia"].id}/').status_code == 200


def test_el_admin_ve_todas_las_producciones(datos):
    ids = {fila['id'] for fila in _filas(_api(datos['admin']).get(URL))}
    assert ids == {datos['propia'].id, datos['ajena'].id, datos['del_admin'].id}
