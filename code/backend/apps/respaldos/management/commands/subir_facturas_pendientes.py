"""`python manage.py subir_facturas_pendientes [--descargar]` (023).

- Sin opciones (arranque del backend en Railway): sube cifradas a R2 las
  facturas del Volume que todavía no estén allí. Nunca falla: el respaldo no
  debe impedir que el backend arranque; los errores quedan en el log.
- `--descargar` (equipo local): copia de R2 a `RESPALDO_CARPETA/facturas/`
  las facturas que falten, tal cual (siguen cifradas).
"""

from django.core.management.base import BaseCommand, CommandError

from apps.respaldos.almacenes import almacen_local, almacen_r2
from apps.respaldos.facturas import (
    descargar_pendientes,
    respaldo_activo,
    subir_pendientes,
)


class Command(BaseCommand):
    help = 'Sube a R2 las facturas que falten, o con --descargar las copia de R2 a la carpeta local.'

    def add_arguments(self, parser):
        parser.add_argument('--descargar', action='store_true')

    def handle(self, *args, descargar, **options):
        if descargar:
            self._descargar()
        else:
            self._subir()

    def _subir(self):
        if not respaldo_activo():
            self.stdout.write('Respaldo de facturas inactivo (sin R2 o sin RESPALDO_PASSWORD).')
            return
        try:
            subidas, errores = subir_pendientes(almacen_r2())
        except Exception as error:  # noqa: BLE001 — nunca impedir que el backend arranque
            self.stderr.write(f'No se pudieron revisar las facturas en R2: {error}')
            return
        self.stdout.write(f'Facturas subidas a R2: {subidas}.' + (f' Con error: {errores}.' if errores else ''))

    def _descargar(self):
        try:
            descargadas = descargar_pendientes(almacen_r2(), almacen_local())
        except Exception as error:
            raise CommandError(f'No se pudieron descargar las facturas de R2: {error}') from error
        self.stdout.write(self.style.SUCCESS(f'Facturas descargadas de R2: {descargadas}.'))
