"""`python manage.py restaurar_respaldo <archivo> --base <nombre>` (023).

Descifra un respaldo de la base y lo restaura en una base **vacía** del mismo
servidor configurado en `DB_*`. Muestra host y base y pide confirmación.
"""

import tempfile
from pathlib import Path

import psycopg2
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.respaldos.cifrado import ErrorCifrado, descifrar_archivo
from apps.respaldos.volcado import (
    ErrorVolcado,
    datos_conexion,
    restaurar_volcado,
    verificar_volcado,
)


def tablas_en_base(base):
    c = datos_conexion(base)
    try:
        conexion = psycopg2.connect(
            host=c['host'], port=c['puerto'], user=c['usuario'], password=c['password'], dbname=c['base'],
            connect_timeout=30,
        )
    except psycopg2.OperationalError as error:
        raise CommandError(f'No se pudo conectar a la base {base}: {error}'.strip()) from error
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                "SELECT count(*) FROM information_schema.tables WHERE table_schema NOT IN ('pg_catalog', 'information_schema')",
            )
            return cursor.fetchone()[0]
    finally:
        conexion.close()


class Command(BaseCommand):
    help = 'Restaura un respaldo cifrado de la base en una base vacía.'

    def add_arguments(self, parser):
        parser.add_argument('archivo', help='Respaldo cifrado (flebosil_*.dump.cifrado).')
        parser.add_argument('--base', required=True, help='Base de destino: debe existir y estar vacía.')
        parser.add_argument('--noinput', action='store_true', help='No pedir confirmación.')

    def handle(self, *args, archivo, base, noinput, **options):
        if not Path(archivo).is_file():
            raise CommandError(f'No existe el archivo {archivo}.')
        if not settings.RESPALDO_PASSWORD:
            raise CommandError('Falta la variable RESPALDO_PASSWORD (contraseña de los respaldos).')

        c = datos_conexion(base)
        if tablas_en_base(base):
            raise CommandError(f'La base {base} no está vacía: restaura solo en una base nueva.')
        if not noinput:
            respuesta = input(f'Se restaurará {Path(archivo).name} en la base {base} de {c["host"]}:{c["puerto"]}. ¿Continuar? [s/N] ')
            if respuesta.strip().lower() not in ('s', 'si', 'sí'):
                raise CommandError('Cancelado.')

        with tempfile.TemporaryDirectory(prefix='flebosil_restaurar_') as carpeta:
            volcado = Path(carpeta) / 'base.dump'
            try:
                descifrar_archivo(archivo, volcado, settings.RESPALDO_PASSWORD)
                entradas = verificar_volcado(volcado)
                restaurar_volcado(volcado, base)
            except (ErrorCifrado, ErrorVolcado) as error:
                raise CommandError(str(error)) from error

        self.stdout.write(self.style.SUCCESS(f'Respaldo restaurado en {base} ({entradas} objetos).'))
