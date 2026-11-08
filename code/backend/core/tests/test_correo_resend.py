"""Backend de correo de Resend (022), sin red: se simula `urlopen`."""

import base64
import io
import json
from unittest import mock
from urllib.error import HTTPError, URLError

import pytest
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMessage, EmailMultiAlternatives, get_connection

from apps.usuarios.serializers import _mensaje_recuperacion
from core.correo_resend import URL_API_RESEND, BackendResend, ErrorResend

BACKEND = 'core.correo_resend.BackendResend'


class _Respuesta(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def _enviar(mensaje, **kwargs):
    """Envía con el backend y devuelve (cantidad, petición enviada a Resend)."""
    with mock.patch('core.correo_resend.urlopen', return_value=_Respuesta(b'{"id": "abc"}')) as urlopen:
        cantidad = get_connection(BACKEND, api_key='re_prueba', **kwargs).send_messages([mensaje])
    peticion = urlopen.call_args.args[0] if urlopen.called else None
    return cantidad, peticion


def test_envia_texto_y_html_con_la_clave_en_la_cabecera():
    mensaje = EmailMultiAlternatives('Asunto', 'Hola', 'FleboSil <no-reply@flebosil.com>', ['ana@ejemplo.com'])
    mensaje.attach_alternative('<p>Hola</p>', 'text/html')

    cantidad, peticion = _enviar(mensaje)

    assert cantidad == 1
    assert peticion.full_url == URL_API_RESEND
    assert peticion.get_method() == 'POST'
    assert peticion.get_header('Authorization') == 'Bearer re_prueba'
    # Resend rechaza el agente por defecto de urllib.
    assert 'urllib' not in peticion.get_header('User-agent').lower()
    assert json.loads(peticion.data) == {
        'from': 'FleboSil <no-reply@flebosil.com>',
        'to': ['ana@ejemplo.com'],
        'subject': 'Asunto',
        'text': 'Hola',
        'html': '<p>Hola</p>',
    }


def test_el_correo_de_recuperacion_lleva_el_logo_embebido():
    cantidad, peticion = _enviar(_mensaje_recuperacion('ana@ejemplo.com', '123456'))

    datos = json.loads(peticion.data)
    assert cantidad == 1
    assert '123456' in datos['text']
    assert 'cid:logo_flebosil' in datos['html']
    [logo] = datos['attachments']
    assert logo['content_id'] == 'logo_flebosil'
    assert logo['filename'] == 'logo_flebosil.png'
    assert logo['content_type'] == 'image/png'
    assert base64.b64decode(logo['content']).startswith(b'\x89PNG')


def test_adjunto_normal_cc_bcc_y_responder_a():
    mensaje = EmailMessage(
        'Factura', 'Adjunta', 'no-reply@flebosil.com', ['a@ejemplo.com'],
        cc=['b@ejemplo.com'], bcc=['c@ejemplo.com'], reply_to=['d@ejemplo.com'],
    )
    mensaje.attach('factura.xml', '<xml/>', 'application/xml')

    _, peticion = _enviar(mensaje)

    datos = json.loads(peticion.data)
    assert datos['cc'] == ['b@ejemplo.com']
    assert datos['bcc'] == ['c@ejemplo.com']
    assert datos['reply_to'] == ['d@ejemplo.com']
    assert datos['attachments'] == [{
        'filename': 'factura.xml',
        'content': base64.b64encode(b'<xml/>').decode(),
        'content_type': 'application/xml',
    }]


def test_un_rechazo_de_resend_se_reporta_con_su_detalle():
    error = HTTPError(URL_API_RESEND, 422, 'Unprocessable', {}, io.BytesIO(b'{"message": "dominio sin verificar"}'))
    mensaje = EmailMessage('A', 'B', 'no-reply@flebosil.com', ['a@ejemplo.com'])

    with (
        mock.patch('core.correo_resend.urlopen', side_effect=error),
        pytest.raises(ErrorResend, match='422.*dominio sin verificar'),
    ):
        BackendResend(api_key='re_prueba').send_messages([mensaje])


def test_con_fail_silently_un_error_de_red_no_interrumpe():
    mensaje = EmailMessage('A', 'B', 'no-reply@flebosil.com', ['a@ejemplo.com'])

    with mock.patch('core.correo_resend.urlopen', side_effect=URLError('sin red')):
        assert BackendResend(api_key='re_prueba', fail_silently=True).send_messages([mensaje]) == 0


def test_sin_clave_no_intenta_enviar(settings):
    settings.RESEND_API_KEY = ''
    mensaje = EmailMessage('A', 'B', 'no-reply@flebosil.com', ['a@ejemplo.com'])

    with (
        mock.patch('core.correo_resend.urlopen') as urlopen,
        pytest.raises(ImproperlyConfigured, match='RESEND_API_KEY'),
    ):
        BackendResend().send_messages([mensaje])
    urlopen.assert_not_called()


def test_toma_la_clave_de_la_configuracion(settings):
    settings.RESEND_API_KEY = 're_de_settings'

    assert BackendResend().api_key == 're_de_settings'
