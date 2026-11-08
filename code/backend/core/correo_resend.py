"""Envío de correo por la API HTTP de Resend (022).

Railway bloquea el SMTP saliente en sus planes bajos, así que en producción
los correos salen por `POST https://api.resend.com/emails`. Se usa `urllib`
de la librería estándar (sin dependencia nueva) y se implementa como backend
de correo de Django, así que el código que arma los mensajes no cambia.

Se activa con `EMAIL_BACKEND=core.correo_resend.BackendResend` y la variable
`RESEND_API_KEY`. Admite texto, HTML y adjuntos, incluidos los embebidos con
`Content-ID` (el logo del correo de recuperación, `cid:logo_flebosil`).
"""

import base64
import json
import logging
from email.message import Message
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail.backends.base import BaseEmailBackend

logger = logging.getLogger(__name__)

URL_API_RESEND = 'https://api.resend.com/emails'
SEGUNDOS_ESPERA = 15


class ErrorResend(Exception):
    """La API de Resend rechazó el correo o no se pudo contactar."""


def _adjunto(adjunto):
    """Convierte un adjunto de `EmailMessage` al formato de Resend.

    Django guarda los adjuntos como tupla `(nombre, contenido, tipo)` o como
    una parte MIME ya armada (así llega el logo, con su `Content-ID`).
    """
    if isinstance(adjunto, Message):
        contenido = adjunto.get_payload(decode=True) or b''
        datos = {
            'filename': adjunto.get_filename() or 'adjunto',
            'content': base64.b64encode(contenido).decode('ascii'),
            'content_type': adjunto.get_content_type(),
        }
        content_id = adjunto.get('Content-ID')
        if content_id:
            datos['content_id'] = content_id.strip().strip('<>')
        return datos

    nombre, contenido, tipo = adjunto
    if isinstance(contenido, str):
        contenido = contenido.encode('utf-8')
    datos = {'filename': nombre, 'content': base64.b64encode(contenido).decode('ascii')}
    if tipo:
        datos['content_type'] = tipo
    return datos


def cuerpo_resend(mensaje):
    """Arma el JSON que espera la API de Resend a partir de un `EmailMessage`."""
    datos = {
        'from': mensaje.from_email or settings.DEFAULT_FROM_EMAIL,
        'to': list(mensaje.to),
        'subject': mensaje.subject,
    }
    if mensaje.cc:
        datos['cc'] = list(mensaje.cc)
    if mensaje.bcc:
        datos['bcc'] = list(mensaje.bcc)
    if mensaje.reply_to:
        datos['reply_to'] = list(mensaje.reply_to)

    if getattr(mensaje, 'content_subtype', 'plain') == 'html':
        datos['html'] = mensaje.body
    elif mensaje.body:
        datos['text'] = mensaje.body
    for contenido, tipo in getattr(mensaje, 'alternatives', []):
        if tipo == 'text/html':
            datos['html'] = contenido

    if mensaje.attachments:
        datos['attachments'] = [_adjunto(a) for a in mensaje.attachments]
    return datos


class BackendResend(BaseEmailBackend):
    """Backend de correo de Django que envía cada mensaje por la API de Resend."""

    def __init__(self, fail_silently=False, api_key=None, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        self.api_key = api_key or getattr(settings, 'RESEND_API_KEY', '')

    def send_messages(self, email_messages):
        if not email_messages:
            return 0
        if not self.api_key:
            raise ImproperlyConfigured('Falta la variable de entorno RESEND_API_KEY para enviar correo con Resend.')

        enviados = 0
        for mensaje in email_messages:
            if not mensaje.recipients():
                continue
            try:
                self._enviar(mensaje)
                enviados += 1
            except ErrorResend:
                if not self.fail_silently:
                    raise
                logger.exception('No se pudo enviar un correo por Resend.')
        return enviados

    def _enviar(self, mensaje):
        peticion = Request(
            URL_API_RESEND,
            data=json.dumps(cuerpo_resend(mensaje)).encode('utf-8'),
            method='POST',
            headers={
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                # Resend rechaza (403) el agente por defecto de urllib.
                'User-Agent': 'FleboSil-ERP/1.0',
            },
        )
        try:
            with urlopen(peticion, timeout=SEGUNDOS_ESPERA) as respuesta:
                respuesta.read()
        except HTTPError as error:
            # El detalle de Resend explica el rechazo (dominio sin verificar,
            # remitente inválido…); nunca incluye la clave.
            detalle = error.read().decode('utf-8', errors='replace')[:500]
            raise ErrorResend(f'Resend respondió {error.code}: {detalle}') from error
        except URLError as error:
            raise ErrorResend(f'No se pudo contactar a Resend: {error.reason}') from error
