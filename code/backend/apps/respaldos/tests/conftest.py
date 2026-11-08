import pytest

from apps.respaldos.almacenes import AlmacenR2


class ClienteR2Falso:
    """Bucket de R2 en memoria, con los métodos de boto3 que se usan."""

    def __init__(self):
        self.objetos = {}

    def upload_file(self, ruta, bucket, clave):
        with open(ruta, 'rb') as archivo:
            self.objetos[clave] = archivo.read()

    def put_object(self, Bucket, Key, Body):  # nombres de boto3
        self.objetos[Key] = bytes(Body)

    def head_object(self, Bucket, Key):
        return {'ContentLength': len(self.objetos[Key])}

    def delete_object(self, Bucket, Key):
        self.objetos.pop(Key, None)

    def download_file(self, bucket, clave, ruta):
        with open(ruta, 'wb') as archivo:
            archivo.write(self.objetos[clave])

    def get_paginator(self, operacion):
        objetos = self.objetos

        class Paginador:
            def paginate(self, Bucket, Prefix):
                claves = sorted(k for k in objetos if k.startswith(Prefix))
                # Dos páginas, para probar que se recorren todas.
                mitad = len(claves) // 2
                for parte in (claves[:mitad], claves[mitad:]):
                    yield {'Contents': [{'Key': k} for k in parte]} if parte else {}

        return Paginador()


@pytest.fixture
def cliente_r2():
    return ClienteR2Falso()


@pytest.fixture
def r2(cliente_r2):
    return AlmacenR2('https://r2.ejemplo', 'flebosil-respaldos', 'id', 'secreto', cliente=cliente_r2)


@pytest.fixture
def password_respaldo(settings):
    settings.RESPALDO_PASSWORD = 'contraseña-de-prueba-123'
    return settings.RESPALDO_PASSWORD

