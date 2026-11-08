import io
import os

import pytest

from apps.respaldos import cifrado
from apps.respaldos.cifrado import (
    ErrorCifrado,
    cifrar_flujo,
    descifrar_archivo,
    descifrar_flujo,
)


@pytest.fixture(autouse=True)
def bloques_chicos(monkeypatch):
    # Bloques de 1 KB para probar varios bloques sin archivos grandes, y
    # scrypt más barato para que las pruebas sean rápidas.
    monkeypatch.setattr(cifrado, 'TAMANO_BLOQUE', 1024)
    monkeypatch.setattr(cifrado, 'LOG2_N_SCRYPT', 10)


def _cifrar(datos, password='clave'):
    salida = io.BytesIO()
    cifrar_flujo(io.BytesIO(datos), salida, password)
    return salida.getvalue()


def _descifrar(datos, password='clave'):
    salida = io.BytesIO()
    descifrar_flujo(io.BytesIO(datos), salida, password)
    return salida.getvalue()


@pytest.mark.parametrize('tamano', [0, 1, 1024, 1025, 5000])
def test_ida_y_vuelta(tamano):
    datos = os.urandom(tamano)

    assert _descifrar(_cifrar(datos)) == datos


def test_el_cifrado_no_revela_el_contenido():
    datos = b'INSERT INTO ventas VALUES (Mercado Libre) ' * 50

    cifrado_ = _cifrar(datos)

    assert b'Mercado Libre' not in cifrado_
    # Sal y nonces aleatorios: el mismo contenido nunca da el mismo archivo.
    assert _cifrar(datos) != cifrado_


def test_contrasena_incorrecta():
    with pytest.raises(ErrorCifrado, match='contraseña es incorrecta'):
        _descifrar(_cifrar(b'datos'), password='otra')


def test_archivo_alterado():
    cifrado_ = bytearray(_cifrar(os.urandom(3000)))
    cifrado_[-10] ^= 0x01

    with pytest.raises(ErrorCifrado):
        _descifrar(bytes(cifrado_))


@pytest.mark.parametrize('cortar', [1, 100, 1500])
def test_archivo_truncado(cortar):
    cifrado_ = _cifrar(os.urandom(3000))

    with pytest.raises(ErrorCifrado):
        _descifrar(cifrado_[:-cortar])


def test_quitar_los_ultimos_bloques_completos_se_detecta():
    # Sin la marca de "último bloque" autenticada, cortar justo en el borde
    # de un bloque daría un archivo válido pero incompleto.
    datos = os.urandom(3000)
    cifrado_ = _cifrar(datos)
    encabezado = len(cifrado.MAGIA) + 1 + cifrado.BYTES_SAL
    primer_bloque = 5 + cifrado.BYTES_NONCE + 1024 + 16

    with pytest.raises(ErrorCifrado):
        _descifrar(cifrado_[: encabezado + primer_bloque])


def test_no_es_un_respaldo():
    with pytest.raises(ErrorCifrado, match='no es un respaldo'):
        _descifrar(b'PGDMP esto es un volcado sin cifrar')


def test_sin_contrasena():
    with pytest.raises(ErrorCifrado, match='RESPALDO_PASSWORD'):
        _cifrar(b'datos', password='')


def test_descifrar_archivo_no_deja_un_archivo_a_medias(tmp_path):
    origen = tmp_path / 'r.cifrado'
    origen.write_bytes(_cifrar(os.urandom(3000)))
    destino = tmp_path / 'r.dump'

    with pytest.raises(ErrorCifrado):
        descifrar_archivo(origen, destino, 'otra')
    assert not destino.exists()
