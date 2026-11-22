"""Avisos por correo a los admins (`001`, "Actualización: centro de
notificaciones y avisos por correo").

- Resumen diario: las secciones de la campana para toda la empresa, a las
  20:00 de Ciudad de México (comando `enviar_resumen_diario`, cron de Railway).
- Avisos inmediatos: stock que llega a 0 y factura que falla al timbrar.

Cada admin activa o desactiva cada tipo en "Información de usuario". Un correo
que falla se registra en el log y nunca interrumpe la operación que lo causó.
"""

import logging
from email.message import MIMEPart

from django.conf import settings
from django.core.cache import cache
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.template.loader import render_to_string
from django.utils import timezone

from apps.usuarios.serializers import RUTA_LOGO_CORREO
from core.permissions import ROL_ADMIN

from .services import armar_notificaciones

logger = logging.getLogger(__name__)

# Un aviso inmediato por elemento al día: la clave vive en la caché (en base
# de datos) un día.
SEGUNDOS_DEDUPLICACION = 24 * 60 * 60


def _url(ruta=''):
    return f'{settings.URL_FRONTEND.rstrip("/")}{ruta}'


def destinatarios(campo_preferencia):
    """Correos de los admins activos con ese tipo de aviso activado."""
    from apps.usuarios.models import Usuario

    return list(
        Usuario.objects.filter(rol_usuario=ROL_ADMIN, is_active=True, **{campo_preferencia: True})
        .exclude(email='')
        .order_by('id')
        .values_list('email', flat=True),
    )


def _mensaje(asunto, texto, plantilla, contexto, para):
    contexto = {
        **contexto,
        'url_app': _url('/dashboard'),
        'url_preferencias': _url('/informacion-usuario'),
    }
    html = render_to_string(plantilla, contexto)
    # Un mensaje por destinatario: nadie ve el correo de los demás.
    mensajes = []
    for correo in para:
        mensaje = EmailMultiAlternatives(
            subject=asunto,
            body=f'{texto}\n\nAbrir FleboSil: {contexto["url_app"]}\n'
            f'Para dejar de recibir estos correos: {contexto["url_preferencias"]}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[correo],
        )
        mensaje.attach_alternative(html, 'text/html')
        with open(RUTA_LOGO_CORREO, 'rb') as archivo_logo:
            logo = MIMEPart()
            logo.set_content(
                archivo_logo.read(), maintype='image', subtype='png',
                disposition='inline', filename='logo_flebosil.png', cid='<logo_flebosil>',
            )
        mensaje.attach(logo)
        mensajes.append(mensaje)
    return mensajes


def _enviar(mensajes):
    enviados = 0
    for mensaje in mensajes:
        try:
            mensaje.send()
            enviados += 1
        except Exception:
            logger.exception('No se pudo enviar el aviso "%s" a %s', mensaje.subject, mensaje.to)
    return enviados


# --- Resumen diario ------------------------------------------------------------


def enviar_resumen_diario(para=None):
    """Envía el resumen a los admins con `recibe_resumen_diario` (o a `para`,
    para pruebas). Devuelve cuántos correos salieron; 0 sin nada que reportar."""

    notificaciones = armar_notificaciones(usuario=None, incluir_nominas=True)
    if not notificaciones['secciones']:
        return 0

    para = para or destinatarios('recibe_resumen_diario')
    if not para:
        return 0

    secciones = [
        {**seccion, 'url': _url(seccion['ruta']), 'elementos': [
            {**elemento, 'url': _url(elemento['ruta'])} for elemento in seccion['elementos']
        ]}
        for seccion in notificaciones['secciones']
    ]
    fecha = timezone.localdate().strftime('%d/%m/%Y')
    contador = notificaciones['contador']
    asunto = f'Resumen del día {fecha} — {contador} pendiente{"s" if contador != 1 else ""} por atender — FleboSil'
    texto = '\n\n'.join(
        f'{seccion["titulo"]} ({seccion["total"]})\n'
        + '\n'.join(
            f'- {e["titulo"]}: {e["detalle"]}' + (f' [{e["etiqueta"]}]' if e['etiqueta'] else '')
            for e in seccion['elementos']
        )
        for seccion in secciones
    )
    mensajes = _mensaje(
        asunto, f'Resumen del día {fecha}\n\n{texto}', 'notificaciones/resumen_diario.html',
        {'fecha': fecha, 'contador': contador, 'secciones': secciones}, para,
    )
    return _enviar(mensajes)


# --- Avisos inmediatos ---------------------------------------------------------


def _aviso_inmediato(clave, asunto, titulo, detalle, ruta, para=None):
    # `cache.add` solo escribe si la clave no existe: el primero del día gana.
    if para is None and not cache.add(f'aviso-critico:{clave}:{timezone.localdate()}', True, SEGUNDOS_DEDUPLICACION):
        return 0
    para = para or destinatarios('recibe_alertas_criticas')
    if not para:
        return 0
    mensajes = _mensaje(
        asunto, f'{titulo}\n{detalle}', 'notificaciones/aviso_inmediato.html',
        {'titulo': titulo, 'detalle': detalle, 'url_elemento': _url(ruta)}, para,
    )
    return _enviar(mensajes)


def _al_confirmar(funcion):
    """Ejecuta el aviso solo si la operación se confirma, y nunca deja que un
    error del aviso afecte a quien lo provocó."""

    def ejecutar():
        try:
            funcion()
        except Exception:
            logger.exception('No se pudo preparar un aviso inmediato')

    transaction.on_commit(ejecutar)


def enviar_aviso_stock_agotado(sucursal_id, tipo_item, item_id, para=None):
    from apps.catalogo.models import MateriaPrima, Producto
    from apps.inventario.models import MovimientoInventario
    from apps.sucursales.models import Sucursal

    if tipo_item == MovimientoInventario.TIPO_PRODUCTO:
        nombre = Producto.objects.get(pk=item_id).nombre_producto
    else:
        nombre = MateriaPrima.objects.get(pk=item_id).nombre_item
    sucursal = Sucursal.objects.get(pk=sucursal_id).nombre_sucursal
    return _aviso_inmediato(
        f'stock:{tipo_item}:{item_id}:{sucursal_id}',
        f'Agotado: {nombre} en {sucursal} — FleboSil',
        f'{nombre} se agotó',
        f'El stock de {nombre} en la sucursal {sucursal} llegó a 0.',
        '/inventario',
        para,
    )


def enviar_aviso_timbrado_fallido(factura_id, para=None):
    from apps.facturacion.models import Factura

    factura = Factura.objects.select_related('venta__cliente').get(pk=factura_id)
    cliente = factura.venta.cliente.nombre_cliente if factura.venta.cliente else 'Sin cliente'
    motivo = factura.mensaje_error or 'El PAC rechazó el timbrado.'
    return _aviso_inmediato(
        f'timbrado:{factura_id}',
        f'Error de timbrado: Factura #{factura_id} — FleboSil',
        f'La factura #{factura_id} no se pudo timbrar',
        f'Venta #{factura.venta_id} · {cliente}. Motivo: {motivo}',
        f'/facturacion/{factura_id}',
        para,
    )


def avisar_stock_agotado(sucursal_id, tipo_item, item_id):
    _al_confirmar(lambda: enviar_aviso_stock_agotado(sucursal_id, tipo_item, item_id))


def avisar_timbrado_fallido(factura_id):
    _al_confirmar(lambda: enviar_aviso_timbrado_fallido(factura_id))
