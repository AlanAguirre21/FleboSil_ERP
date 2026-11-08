"""Copia cifrada de los XML/PDF de las facturas en R2 (023).

Las facturas viven en el Volume del backend, que el trabajo programado de
respaldo no puede ver. Por eso cada archivo se sube al generarse y, al
arrancar el backend, se suben los que falten. Un CFDI timbrado no cambia, así
que cada archivo se sube una sola vez y no rota.
"""

import io
import logging
import os

from django.conf import settings

from .almacenes import PREFIJO_FACTURAS, almacen_r2, r2_configurado
from .cifrado import cifrar_flujo

logger = logging.getLogger(__name__)

EXTENSION = '.cifrado'


def respaldo_activo():
    """Sin R2 o sin contraseña (local, pruebas) no se respalda nada."""
    return r2_configurado() and bool(settings.RESPALDO_PASSWORD)


def clave_factura(nombre_archivo):
    return f'{PREFIJO_FACTURAS}{nombre_archivo}{EXTENSION}'


def _subir(almacen, ruta_absoluta):
    with open(ruta_absoluta, 'rb') as entrada:
        cifrado = io.BytesIO()
        cifrar_flujo(entrada, cifrado, settings.RESPALDO_PASSWORD)
    almacen.guardar_bytes(cifrado.getvalue(), clave_factura(os.path.basename(ruta_absoluta)))


def respaldar_factura(ruta_relativa):
    """Sube un archivo de factura (`facturas/<id>.xml`). Nunca lanza: el
    respaldo no debe impedir timbrar; si falla, lo recupera el siguiente
    arranque con `subir_facturas_pendientes`."""
    if not respaldo_activo():
        return
    try:
        _subir(almacen_r2(), os.path.join(settings.MEDIA_ROOT, ruta_relativa))
    except Exception:
        logger.exception('No se pudo respaldar en R2 la factura %s; se reintentará al arrancar.', ruta_relativa)


def carpeta_facturas():
    return os.path.join(settings.MEDIA_ROOT, 'facturas')


def subir_pendientes(almacen):
    """Sube las facturas locales que no estén en el almacén. Devuelve (subidas, errores)."""
    carpeta = carpeta_facturas()
    if not os.path.isdir(carpeta):
        return 0, 0
    existentes = set(almacen.listar(PREFIJO_FACTURAS))
    subidas = errores = 0
    for nombre in sorted(os.listdir(carpeta)):
        ruta = os.path.join(carpeta, nombre)
        if not os.path.isfile(ruta) or clave_factura(nombre) in existentes:
            continue
        try:
            _subir(almacen, ruta)
            subidas += 1
        except Exception:
            errores += 1
            logger.exception('No se pudo respaldar en R2 la factura %s.', nombre)
    return subidas, errores


def descargar_pendientes(origen, destino):
    """Copia (sin descifrar) las facturas del origen que falten en el destino."""
    existentes = set(destino.listar(PREFIJO_FACTURAS))
    descargadas = 0
    for clave in origen.listar(PREFIJO_FACTURAS):
        if clave in existentes:
            continue
        ruta_local = destino.ruta(clave)
        ruta_local.parent.mkdir(parents=True, exist_ok=True)
        temporal = ruta_local.with_name(ruta_local.name + '.parcial')
        origen.descargar(clave, temporal)
        os.replace(temporal, ruta_local)
        descargadas += 1
    return descargadas
