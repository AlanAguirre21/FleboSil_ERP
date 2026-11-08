"""Destinos de los respaldos (023): Cloudflare R2 y una carpeta local.

Los dos exponen lo mismo, con claves tipo `base/<archivo>` y
`facturas/<archivo>`: en R2 son las claves del bucket; en la carpeta local,
subcarpetas.
"""

import os
import shutil
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

PREFIJO_BASE = 'base/'
PREFIJO_FACTURAS = 'facturas/'


class AlmacenLocal:
    """Carpeta del equipo local (opción B)."""

    def __init__(self, carpeta):
        self.carpeta = Path(carpeta)

    def __str__(self):
        return f'carpeta {self.carpeta}'

    def ruta(self, clave):
        ruta = (self.carpeta / clave).resolve()
        if self.carpeta.resolve() not in ruta.parents:
            raise ValueError(f'Clave fuera de la carpeta de respaldos: {clave}')
        return ruta

    def guardar(self, archivo_local, clave):
        destino = self.ruta(clave)
        destino.parent.mkdir(parents=True, exist_ok=True)
        # Se copia a un temporal y se renombra: un corte a la mitad nunca deja
        # un respaldo incompleto con nombre válido.
        temporal = destino.with_name(destino.name + '.parcial')
        shutil.copyfile(archivo_local, temporal)
        os.replace(temporal, destino)

    def guardar_bytes(self, datos, clave):
        destino = self.ruta(clave)
        destino.parent.mkdir(parents=True, exist_ok=True)
        temporal = destino.with_name(destino.name + '.parcial')
        temporal.write_bytes(datos)
        os.replace(temporal, destino)

    def listar(self, prefijo):
        carpeta = self.ruta(prefijo) if prefijo else self.carpeta
        if not carpeta.is_dir():
            return []
        return sorted(f'{prefijo}{a.name}' for a in carpeta.iterdir() if a.is_file() and not a.name.endswith('.parcial'))

    def tamano(self, clave):
        return self.ruta(clave).stat().st_size

    def borrar(self, clave):
        self.ruta(clave).unlink(missing_ok=True)

    def descargar(self, clave, archivo_local):
        shutil.copyfile(self.ruta(clave), archivo_local)


class AlmacenR2:
    """Bucket de Cloudflare R2 por su API compatible con S3 (opción A)."""

    def __init__(self, endpoint, bucket, access_key_id, secret_access_key, cliente=None):
        self.bucket = bucket
        if cliente is None:
            import boto3  # solo se carga si hay R2 configurado
            from botocore.config import Config

            cliente = boto3.client(
                's3',
                endpoint_url=endpoint,
                aws_access_key_id=access_key_id,
                aws_secret_access_key=secret_access_key,
                region_name='auto',
                config=Config(retries={'max_attempts': 5, 'mode': 'standard'}),
            )
        self.cliente = cliente

    def __str__(self):
        return f'bucket R2 {self.bucket}'

    def guardar(self, archivo_local, clave):
        self.cliente.upload_file(str(archivo_local), self.bucket, clave)

    def guardar_bytes(self, datos, clave):
        self.cliente.put_object(Bucket=self.bucket, Key=clave, Body=datos)

    def listar(self, prefijo):
        claves = []
        paginador = self.cliente.get_paginator('list_objects_v2')
        for pagina in paginador.paginate(Bucket=self.bucket, Prefix=prefijo):
            claves.extend(objeto['Key'] for objeto in pagina.get('Contents', []))
        return sorted(claves)

    def tamano(self, clave):
        return self.cliente.head_object(Bucket=self.bucket, Key=clave)['ContentLength']

    def borrar(self, clave):
        self.cliente.delete_object(Bucket=self.bucket, Key=clave)

    def descargar(self, clave, archivo_local):
        self.cliente.download_file(self.bucket, clave, str(archivo_local))


def r2_configurado():
    return all(
        getattr(settings, nombre, '')
        for nombre in ('R2_ENDPOINT', 'R2_BUCKET', 'R2_ACCESS_KEY_ID', 'R2_SECRET_ACCESS_KEY')
    )


def almacen_r2():
    if not r2_configurado():
        raise ImproperlyConfigured(
            'Faltan variables de R2 (R2_ENDPOINT, R2_BUCKET, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY).',
        )
    return AlmacenR2(
        settings.R2_ENDPOINT, settings.R2_BUCKET, settings.R2_ACCESS_KEY_ID, settings.R2_SECRET_ACCESS_KEY,
    )


def almacen_local():
    if not settings.RESPALDO_CARPETA:
        raise ImproperlyConfigured('Falta la variable RESPALDO_CARPETA (carpeta local de respaldos).')
    return AlmacenLocal(settings.RESPALDO_CARPETA)


def almacen(destino):
    return almacen_r2() if destino == 'r2' else almacen_local()
