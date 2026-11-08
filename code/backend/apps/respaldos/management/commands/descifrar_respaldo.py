"""`python manage.py descifrar_respaldo <archivo> --salida <ruta>` (023).

Descifra cualquier archivo de respaldo: un volcado de la base (`.dump`, para
`pg_restore`) o una factura (`.xml`/`.pdf`).
"""

from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.respaldos.cifrado import ErrorCifrado, descifrar_archivo


class Command(BaseCommand):
    help = 'Descifra un archivo de respaldo (base o factura).'

    def add_arguments(self, parser):
        parser.add_argument('archivo')
        parser.add_argument('--salida', required=True, help='Ruta del archivo descifrado.')

    def handle(self, *args, archivo, salida, **options):
        if not Path(archivo).is_file():
            raise CommandError(f'No existe el archivo {archivo}.')
        if Path(salida).exists():
            raise CommandError(f'Ya existe {salida}: elige otra ruta de salida.')
        if not settings.RESPALDO_PASSWORD:
            raise CommandError('Falta la variable RESPALDO_PASSWORD (contraseña de los respaldos).')
        try:
            descifrar_archivo(archivo, salida, settings.RESPALDO_PASSWORD)
        except ErrorCifrado as error:
            raise CommandError(str(error)) from error
        self.stdout.write(self.style.SUCCESS(f'Descifrado en {salida}.'))
