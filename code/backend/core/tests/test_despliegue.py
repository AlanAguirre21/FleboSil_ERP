"""Comportamiento de producción (022): salud, fotos sin DEBUG, IP real."""

import pytest
from django.core.cache import cache
from django.test import Client

from apps.usuarios.models import RegistroAcceso, Usuario


@pytest.fixture
def cliente():
    # Sin `DEBUG` (pytest-django ya lo apaga): así se comporta en producción.
    return Client()


def test_salud_responde_sin_sesion_ni_base(cliente):
    respuesta = cliente.get('/salud/')

    assert respuesta.status_code == 200
    assert respuesta.json() == {'estado': 'ok'}


@pytest.mark.parametrize(
    ('url', 'carpeta'),
    [('/fotos-empleados/', 'EMPLEADOS_FOTOS_ROOT'), ('/fotos-usuarios/', 'USUARIOS_FOTOS_ROOT')],
)
def test_las_fotos_se_sirven_sin_debug(cliente, settings, tmp_path, url, carpeta):
    setattr(settings, carpeta, tmp_path)
    (tmp_path / 'foto.png').write_bytes(b'\x89PNG prueba')

    respuesta = cliente.get(f'{url}foto.png')

    assert respuesta.status_code == 200
    assert b''.join(respuesta.streaming_content) == b'\x89PNG prueba'


def test_no_se_puede_salir_de_la_carpeta_de_fotos(cliente, settings, tmp_path):
    settings.EMPLEADOS_FOTOS_ROOT = tmp_path / 'fotos'
    (tmp_path / 'fotos').mkdir()
    (tmp_path / 'secreto.txt').write_text('no')

    # Django rechaza la ruta sospechosa (400) o no la encuentra (404): nunca la sirve.
    for url in ('/fotos-empleados/../secreto.txt', '/fotos-empleados/%2e%2e/secreto.txt'):
        assert cliente.get(url).status_code in (400, 404)


def test_los_archivos_de_facturacion_no_tienen_url_publica(cliente, settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    (tmp_path / 'facturas').mkdir()
    (tmp_path / 'facturas' / 'f.xml').write_text('<cfdi/>')

    assert cliente.get('/media/facturas/f.xml').status_code == 404


@pytest.mark.django_db
def test_el_login_registra_la_ip_real_detras_del_proxy(cliente, settings):
    settings.NUM_PROXIES = 1
    cache.clear()
    Usuario.objects.create_user(username='ana', email='ana@ejemplo.com', password='clave-segura-123')

    respuesta = cliente.post(
        '/api/auth/login/',
        {'email': 'ana@ejemplo.com', 'password': 'clave-segura-123'},
        content_type='application/json',
        REMOTE_ADDR='10.0.0.1',
        HTTP_X_FORWARDED_FOR='1.1.1.1, 200.10.20.30',
    )

    assert respuesta.status_code == 200
    assert RegistroAcceso.objects.get(usuario__email='ana@ejemplo.com').ip == '200.10.20.30'


@pytest.mark.django_db
def test_el_limite_de_login_cuenta_por_la_ip_real(cliente, settings):
    settings.NUM_PROXIES = 1
    cache.clear()

    def intento(ip_real):
        return cliente.post(
            '/api/auth/login/',
            {'email': 'nadie@ejemplo.com', 'password': 'x'},
            content_type='application/json',
            REMOTE_ADDR='10.0.0.1',  # siempre el balanceador
            HTTP_X_FORWARDED_FOR=ip_real,
        ).status_code

    assert [intento('200.0.0.1') for _ in range(5)] == [401] * 5
    assert intento('200.0.0.1') == 429
    # Otro cliente detrás del mismo balanceador no queda bloqueado.
    assert intento('200.0.0.2') == 401


def test_una_url_inexistente_responde_json(cliente):
    respuesta = cliente.get('/api/no-existe/')

    assert respuesta.status_code == 404
    assert respuesta.json() == {'detail': 'No se encontró el recurso solicitado.'}


def test_un_error_fuera_de_drf_responde_json_sin_detalles(settings):
    from django.test import RequestFactory

    from core.excepciones import error_servidor

    respuesta = error_servidor(RequestFactory().get('/'))

    assert respuesta.status_code == 500
    assert 'Traceback' not in respuesta.content.decode()
    assert 'detail' in respuesta.content.decode()
