"""Administrador protegido admin@flebosil.com — feature 022."""

from datetime import timedelta

import pytest
from django.core import mail
from django.core.cache import cache
from django.core.management import call_command
from django.core.management.base import CommandError
from django.utils import timezone
from rest_framework.test import APIClient

from apps.usuarios.models import CodigoRecuperacion, Usuario

EMAIL = 'admin@flebosil.com'
CLAVE = 'clave-control-789'


@pytest.fixture
def con_clave(monkeypatch):
    monkeypatch.setenv('ADMIN_PASSWORD', CLAVE)


@pytest.fixture
def protegido(db, con_clave):
    call_command('asegurar_admin')
    return Usuario.objects.get(email=EMAIL)


@pytest.fixture
def otro_admin(db):
    return Usuario.objects.create_user(
        username='admin2', email='admin2@flebosil.test', password='clave-segura-123', rol_usuario='admin',
    )


def _cliente(usuario):
    client = APIClient()
    client.force_authenticate(user=usuario)
    return client


# --- Comando asegurar_admin ------------------------------------------------


@pytest.mark.django_db
def test_crea_el_admin_protegido(con_clave):
    call_command('asegurar_admin')

    usuario = Usuario.objects.get(email=EMAIL)
    assert usuario.rol_usuario == 'admin'
    assert usuario.is_active and usuario.is_staff and usuario.is_superuser
    assert usuario.check_password(CLAVE)


@pytest.mark.django_db
def test_restaura_cambios_hechos_fuera_de_la_api(protegido):
    Usuario.objects.filter(pk=protegido.pk).update(rol_usuario='operador', is_active=False)
    protegido.refresh_from_db()
    protegido.set_password('otra-cosa-000')
    protegido.save()

    call_command('asegurar_admin')

    protegido.refresh_from_db()
    assert protegido.rol_usuario == 'admin'
    assert protegido.is_active
    assert protegido.check_password(CLAVE)


@pytest.mark.django_db
def test_es_idempotente(protegido):
    call_command('asegurar_admin')
    assert Usuario.objects.filter(email=EMAIL).count() == 1


@pytest.mark.django_db
def test_falla_sin_admin_password(monkeypatch):
    monkeypatch.delenv('ADMIN_PASSWORD', raising=False)
    with pytest.raises(CommandError, match='ADMIN_PASSWORD'):
        call_command('asegurar_admin')
    assert not Usuario.objects.filter(email=EMAIL).exists()


# --- Bloqueos en la API ----------------------------------------------------


@pytest.mark.django_db
def test_otro_admin_no_puede_cambiar_su_correo_ni_rol(protegido, otro_admin):
    client = _cliente(otro_admin)
    for cambio in ({'email': 'otro@flebosil.com'}, {'rol_usuario': 'operador'}):
        response = client.patch(f'/api/usuarios/{protegido.id}/', cambio, format='json')
        assert response.status_code == 403
        assert 'administrador de control' in response.data['detail']
    protegido.refresh_from_db()
    assert protegido.email == EMAIL
    assert protegido.rol_usuario == 'admin'


@pytest.mark.django_db
def test_otro_admin_no_puede_desactivarlo(protegido, otro_admin):
    response = _cliente(otro_admin).delete(f'/api/usuarios/{protegido.id}/')

    assert response.status_code == 400
    assert 'administrador de control' in response.data['detail']
    protegido.refresh_from_db()
    assert protegido.is_active


@pytest.mark.django_db
def test_el_mismo_no_puede_cambiar_su_correo_ni_rol(protegido, otro_admin):
    client = _cliente(protegido)
    for cambio in ({'email': 'otro@flebosil.com'}, {'rol_usuario': 'operador'}):
        response = client.patch('/api/usuarios/me/', cambio, format='json')
        assert response.status_code == 403
    protegido.refresh_from_db()
    assert protegido.email == EMAIL
    assert protegido.rol_usuario == 'admin'


@pytest.mark.django_db
def test_nombre_si_se_puede_editar(protegido, otro_admin):
    response = _cliente(protegido).patch(
        '/api/usuarios/me/', {'first_name': 'Control', 'last_name': 'FleboSil', 'email': EMAIL}, format='json',
    )

    assert response.status_code == 200
    protegido.refresh_from_db()
    assert protegido.first_name == 'Control'


@pytest.mark.django_db
def test_recuperar_contrasena_no_genera_codigo(protegido):
    cache.clear()
    response = APIClient().post('/api/auth/recuperar/', {'email': EMAIL}, format='json')

    assert response.status_code == 200   # misma respuesta que con un correo inexistente
    assert not CodigoRecuperacion.objects.filter(usuario=protegido).exists()
    assert len(mail.outbox) == 0


@pytest.mark.django_db
def test_cambiar_contrasena_por_recuperacion_se_rechaza(protegido):
    cache.clear()
    CodigoRecuperacion.objects.create(
        usuario=protegido, codigo='123456', expira_en=timezone.now() + timedelta(minutes=10), verificado=True,
    )
    response = APIClient().post(
        '/api/auth/cambiar-contrasena/',
        {'email': EMAIL, 'password': 'clave-nueva-456', 'password_confirmacion': 'clave-nueva-456'},
        format='json',
    )

    assert response.status_code == 403
    protegido.refresh_from_db()
    assert protegido.check_password(CLAVE)


@pytest.mark.django_db
def test_admin_de_django_no_lo_edita_ni_borra(protegido, otro_admin):
    otro_admin.is_staff = otro_admin.is_superuser = True
    otro_admin.save()
    client = APIClient()
    client.force_login(otro_admin)

    assert client.get(f'/admin/usuarios/usuario/{protegido.id}/delete/').status_code == 403
    response = client.post(f'/admin/usuarios/usuario/{protegido.id}/change/', {'email': 'x@flebosil.com'})
    assert response.status_code == 403
    protegido.refresh_from_db()
    assert protegido.email == EMAIL
