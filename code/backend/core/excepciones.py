import logging

from django.db import DataError
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger('django.request')

MENSAJE_VALOR_EXCEDIDO = 'Uno de los valores numéricos excede el máximo permitido. Revisa las cantidades y montos.'
MENSAJE_ERROR_INTERNO = 'Ocurrió un error interno en el servidor. Intenta de nuevo o contacta a un administrador.'


def manejador_excepciones(exc, context):
    """Garantiza que toda respuesta de error de la API sea JSON
    `{"detail": "..."}` (constitución, "API errors") — también para
    excepciones que DRF no maneja por sí mismo, que de otro modo llegarían
    como la página HTML de error 500 de Django.

    `DataError` (ej. un total que excede los dígitos de su columna
    `Decimal`) es un error del dato enviado, no del servidor: se responde
    400. Cualquier otra excepción no manejada se registra con su traceback
    completo en el log y se responde 500 sin exponer detalles internos.
    """
    respuesta = exception_handler(exc, context)
    if respuesta is not None:
        return respuesta

    if isinstance(exc, DataError):
        logger.warning('Valor fuera de rango en %s: %s', context['request'].path, exc)
        return Response({'detail': MENSAJE_VALOR_EXCEDIDO}, status=400)

    logger.error('Error no manejado en %s', context['request'].path, exc_info=exc)
    return Response({'detail': MENSAJE_ERROR_INTERNO}, status=500)
