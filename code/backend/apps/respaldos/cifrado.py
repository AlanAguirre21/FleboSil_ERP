"""Cifrado de respaldos con contraseña (023).

Formato del archivo cifrado:

    MAGIA (8 bytes) · log2(N) de scrypt (1 byte) · sal (16 bytes)
    y luego bloques: final (1 byte) · largo (4 bytes) · nonce (12 bytes) · datos cifrados

La clave sale de la contraseña con scrypt y una sal aleatoria por archivo; cada
bloque (1 MB de datos) se cifra con AES-256-GCM, que además autentica: una
contraseña incorrecta o un archivo alterado se detectan al descifrar. El
encabezado, el número de bloque y la marca de "último bloque" van como datos
asociados, así que reordenar, quitar o truncar bloques también se detecta. Se
procesa por bloques para no cargar el volcado completo en memoria.
"""

import os
import struct

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

MAGIA = b'FLBRSP01'
LOG2_N_SCRYPT = 15  # N = 32768: ~0.1 s y 32 MB de memoria por archivo.
BYTES_SAL = 16
BYTES_NONCE = 12
TAMANO_BLOQUE = 1024 * 1024
_ENCABEZADO_BLOQUE = struct.Struct('>BI')  # final, largo del bloque cifrado

MENSAJE_NO_SE_PUDO_DESCIFRAR = 'No se pudo descifrar: la contraseña es incorrecta o el archivo está dañado.'


class ErrorCifrado(Exception):
    """El archivo no es un respaldo válido o la contraseña no corresponde."""


def _clave(password, sal, log2_n):
    if not password:
        raise ErrorCifrado('Falta la contraseña de respaldos (RESPALDO_PASSWORD).')
    return Scrypt(salt=sal, length=32, n=2 ** log2_n, r=8, p=1).derive(password.encode('utf-8'))


def _datos_asociados(encabezado, indice, final):
    return encabezado + struct.pack('>QB', indice, final)


def cifrar_flujo(entrada, salida, password):
    """Cifra todo lo que se lea de `entrada` y lo escribe en `salida`."""
    sal = os.urandom(BYTES_SAL)
    encabezado = MAGIA + bytes([LOG2_N_SCRYPT]) + sal
    aes = AESGCM(_clave(password, sal, LOG2_N_SCRYPT))
    salida.write(encabezado)

    indice = 0
    bloque = entrada.read(TAMANO_BLOQUE)
    while True:
        siguiente = entrada.read(TAMANO_BLOQUE)
        final = 0 if siguiente else 1
        nonce = os.urandom(BYTES_NONCE)
        cifrado = aes.encrypt(nonce, bloque, _datos_asociados(encabezado, indice, final))
        salida.write(_ENCABEZADO_BLOQUE.pack(final, len(cifrado)) + nonce + cifrado)
        if final:
            return
        bloque = siguiente
        indice += 1


def descifrar_flujo(entrada, salida, password):
    """Descifra un respaldo de `entrada` hacia `salida`. Lanza `ErrorCifrado`
    si la contraseña no corresponde o el archivo está alterado o incompleto."""
    encabezado = entrada.read(len(MAGIA) + 1 + BYTES_SAL)
    if len(encabezado) != len(MAGIA) + 1 + BYTES_SAL or not encabezado.startswith(MAGIA):
        raise ErrorCifrado('El archivo no es un respaldo cifrado de FleboSil.')
    log2_n = encabezado[len(MAGIA)]
    aes = AESGCM(_clave(password, encabezado[len(MAGIA) + 1:], log2_n))

    indice = 0
    while True:
        cabecera = entrada.read(_ENCABEZADO_BLOQUE.size)
        if len(cabecera) != _ENCABEZADO_BLOQUE.size:
            raise ErrorCifrado('El archivo está incompleto (le faltan datos al final).')
        final, largo = _ENCABEZADO_BLOQUE.unpack(cabecera)
        nonce = entrada.read(BYTES_NONCE)
        cifrado = entrada.read(largo)
        if final not in (0, 1) or len(nonce) != BYTES_NONCE or len(cifrado) != largo:
            raise ErrorCifrado('El archivo está incompleto o dañado.')
        try:
            salida.write(aes.decrypt(nonce, cifrado, _datos_asociados(encabezado, indice, final)))
        except InvalidTag as error:
            raise ErrorCifrado(MENSAJE_NO_SE_PUDO_DESCIFRAR) from error
        if final:
            if entrada.read(1):
                raise ErrorCifrado('El archivo tiene datos de más después del último bloque.')
            return
        indice += 1


def cifrar_archivo(origen, destino, password):
    with open(origen, 'rb') as entrada, open(destino, 'wb') as salida:
        cifrar_flujo(entrada, salida, password)


def descifrar_archivo(origen, destino, password):
    """Descifra a `destino`; si falla, no deja un archivo a medias."""
    try:
        with open(origen, 'rb') as entrada, open(destino, 'wb') as salida:
            descifrar_flujo(entrada, salida, password)
    except BaseException:
        if os.path.exists(destino):
            os.remove(destino)
        raise
