"""Volver a registrar un usuario desactivado, y correos que solo difieren
en mayúsculas — una cuenta "borrada" solo queda con `is_active=False`."""

import pytest
from django.db import IntegrityError, transaction
from rest_framework.test import APIClient

from apps.rrhh.models import Empleado
from apps.usuarios.models import Usuario

CLAVE = 'Clave-Segura-2026!'


@pytest.fixture
def admin_client(db):
    admin = Usuario.objects.create_user(
        username='admin1', email='admin1@flebosil.test', password=CLAVE, rol_usuario='admin',
    )
    client = APIClient()
    client.force_authenticate(user=admin)
    return client


def _crear(client, **extra):
    datos = {
        'email': 'juan@flebosil.test', 'first_name': 'Juan', 'last_name': 'Pérez',
        'rol_usuario': 'operador', 'password': CLAVE,
    }
    datos.update(extra)
    return client.post('/api/usuarios/', datos, format='json')


def _crear_y_desactivar(client, **extra):
    respuesta = _crear(client, **extra)
    assert respuesta.status_code == 201
    assert client.delete(f'/api/usuarios/{respuesta.data["id"]}/').status_code == 204
    return respuesta.data['id']


@pytest.mark.django_db
def test_recrear_un_usuario_desactivado_indica_que_se_puede_reactivar(admin_client):
    _crear_y_desactivar(admin_client)

    respuesta = _crear(admin_client)

    assert respuesta.status_code == 400
    mensaje = respuesta.data['email'][0]
    assert 'desactivado' in mensaje
    assert 'juan@flebosil.test' in mensaje
    assert 'Reactívalo' in mensaje


@pytest.mark.django_db
def test_duplicado_activo_responde_mensaje_en_espanol(admin_client):
    _crear(admin_client)

    respuesta = _crear(admin_client)

    assert respuesta.status_code == 400
    assert respuesta.data['email'][0] == 'Ya existe un usuario con ese correo electrónico.'


@pytest.mark.django_db
def test_el_mismo_correo_con_mayusculas_no_crea_otra_cuenta(admin_client):
    _crear_y_desactivar(admin_client)

    respuesta = _crear(admin_client, email='Juan@Flebosil.TEST')

    assert respuesta.status_code == 400
    assert Usuario.objects.filter(email__iexact='juan@flebosil.test').count() == 1


@pytest.mark.django_db
def test_el_correo_se_guarda_en_minusculas(admin_client):
    respuesta = _crear(admin_client, email='  Maria@Flebosil.Test ')

    assert respuesta.status_code == 201
    assert respuesta.data['email'] == 'maria@flebosil.test'
    assert respuesta.data['username'] == 'maria@flebosil.test'


@pytest.mark.django_db
def test_login_no_distingue_mayusculas(admin_client):
    _crear(admin_client, email='maria@flebosil.test')

    respuesta = APIClient().post(
        '/api/auth/login/', {'email': 'MARIA@flebosil.test', 'password': CLAVE}, format='json',
    )

    assert respuesta.status_code == 200
    assert 'access' in respuesta.data


@pytest.mark.django_db
def test_la_base_de_datos_rechaza_correos_que_solo_difieren_en_mayusculas(db):
    Usuario.objects.create_user(username='a', email='ana@flebosil.test', password=CLAVE)
    # `save()` ya normaliza; se fuerza el valor con `update()` para probar
    # la restricción de la base de datos por sí misma.
    otro = Usuario.objects.create_user(username='b', email='otra@flebosil.test', password=CLAVE)
    with pytest.raises(IntegrityError), transaction.atomic():
        Usuario.objects.filter(pk=otro.pk).update(email='ANA@flebosil.test')


@pytest.mark.django_db
def test_empleado_con_cuenta_desactivada_indica_que_se_puede_reactivar(admin_client):
    empleado = Empleado.objects.create(nombre_completo='Juan Pérez')
    _crear_y_desactivar(admin_client, empleado=empleado.id)

    respuesta = _crear(admin_client, email='juan.nuevo@flebosil.test', empleado=empleado.id)

    assert respuesta.status_code == 400
    assert 'desactivado' in respuesta.data['empleado'][0]


@pytest.mark.django_db
def test_username_ocupado_por_cuenta_desactivada(admin_client):
    _crear_y_desactivar(admin_client)

    respuesta = _crear(admin_client, email='otro@flebosil.test', username='juan@flebosil.test')

    assert respuesta.status_code == 400
    assert 'desactivado' in respuesta.data['username'][0]


@pytest.mark.django_db
def test_username_por_defecto_ocupado_responde_400_y_no_error_500(admin_client):
    # Una cuenta cuyo `username` es un correo que ya no usa como `email`.
    Usuario.objects.create_user(username='libre@flebosil.test', email='viejo@flebosil.test', password=CLAVE)

    respuesta = _crear(admin_client, email='libre@flebosil.test')

    assert respuesta.status_code == 400
    assert 'username' in respuesta.data


@pytest.mark.django_db
def test_editar_un_usuario_sin_cambiar_correo_no_choca_consigo_mismo(admin_client):
    usuario_id = _crear(admin_client).data['id']

    respuesta = admin_client.patch(
        f'/api/usuarios/{usuario_id}/', {'email': 'JUAN@flebosil.test', 'first_name': 'Juanito'}, format='json',
    )

    assert respuesta.status_code == 200
    assert respuesta.data['email'] == 'juan@flebosil.test'


@pytest.mark.django_db
def test_reactivar_recupera_la_cuenta_original(admin_client):
    usuario_id = _crear_y_desactivar(admin_client)

    respuesta = admin_client.post(f'/api/usuarios/{usuario_id}/reactivar/')

    assert respuesta.status_code == 200
    assert respuesta.data['activo'] is True
