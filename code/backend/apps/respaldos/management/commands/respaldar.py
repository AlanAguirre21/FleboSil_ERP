"""`python manage.py respaldar --destino r2|local` (023).

Vuelca la base, comprueba el volcado, lo cifra con `RESPALDO_PASSWORD`, lo
guarda en el destino y aplica la regla de conservación (12 semanales + el
primero de cada mes durante 12 meses). Si algo falla, no borra ningún
respaldo anterior, avisa por correo a `RESPALDO_AVISO_EMAIL` y termina con
error. Nunca imprime contraseñas ni claves.
"""

import tempfile
from pathlib import Path

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from apps.respaldos.almacenes import PREFIJO_BASE, almacen
from apps.respaldos.cifrado import cifrar_archivo
from apps.respaldos.conservacion import nombre_respaldo, nombres_a_borrar
from apps.respaldos.volcado import datos_conexion, verificar_volcado, volcar_base

DESTINOS = {'r2': 'Cloudflare R2', 'local': 'equipo local'}


def _tamano_legible(bytes_):
    for unidad in ('B', 'KB', 'MB', 'GB'):
        if bytes_ < 1024 or unidad == 'GB':
            return f'{bytes_:.0f} {unidad}' if unidad == 'B' else f'{bytes_:.1f} {unidad}'
        bytes_ /= 1024
    return f'{bytes_} B'


class Command(BaseCommand):
    help = 'Respalda la base de datos, cifrada, en R2 o en la carpeta local, y rota los respaldos viejos.'

    def add_arguments(self, parser):
        parser.add_argument('--destino', choices=sorted(DESTINOS), required=True)

    def handle(self, *args, destino, **options):
        try:
            resumen = self._respaldar(destino)
        except Exception as error:
            mensaje = str(error) or error.__class__.__name__
            self._avisar_fallo(destino, mensaje)
            raise CommandError(f'Falló el respaldo ({DESTINOS[destino]}): {mensaje}') from error
        self.stdout.write(self.style.SUCCESS(resumen))

    def _respaldar(self, destino):
        if not settings.RESPALDO_PASSWORD:
            raise CommandError('Falta la variable RESPALDO_PASSWORD (contraseña de los respaldos).')
        donde = almacen(destino)
        conexion = datos_conexion()
        nombre = nombre_respaldo(timezone.localtime())
        self.stdout.write(f'Respaldando la base {conexion["base"]} de {conexion["host"]} en {donde}...')

        with tempfile.TemporaryDirectory(prefix='flebosil_respaldo_') as carpeta:
            volcado = Path(carpeta) / 'base.dump'
            cifrado = Path(carpeta) / nombre
            volcar_base(volcado)
            entradas = verificar_volcado(volcado)
            cifrar_archivo(volcado, cifrado, settings.RESPALDO_PASSWORD)
            tamano = cifrado.stat().st_size
            donde.guardar(cifrado, f'{PREFIJO_BASE}{nombre}')

        # Solo después de guardar el nuevo con éxito se borra lo que sobra.
        existentes = [clave.removeprefix(PREFIJO_BASE) for clave in donde.listar(PREFIJO_BASE)]
        borrados = nombres_a_borrar(existentes)
        for viejo in borrados:
            donde.borrar(f'{PREFIJO_BASE}{viejo}')

        lineas = [
            f'Respaldo guardado: {nombre} ({_tamano_legible(tamano)}, {entradas} objetos de la base).',
            f'Respaldos en {DESTINOS[destino]}: {len(existentes) - len(borrados)}.',
        ]
        if borrados:
            lineas.append('Borrados por antigüedad: ' + ', '.join(borrados) + '.')
        return '\n'.join(lineas)

    def _avisar_fallo(self, destino, mensaje):
        if not settings.RESPALDO_AVISO_EMAIL:
            return
        try:
            send_mail(
                subject=f'Falló el respaldo de FleboSil ({DESTINOS[destino]})',
                message=(
                    f'El respaldo semanal de la base de datos en {DESTINOS[destino]} no se completó.\n\n'
                    f'Error: {mensaje}\n\n'
                    'Los respaldos anteriores no se tocaron. Revisa el registro del trabajo y vuelve a correrlo.'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.RESPALDO_AVISO_EMAIL],
            )
        except Exception as error:  # noqa: BLE001 — el aviso no debe ocultar el error original
            self.stderr.write(f'Tampoco se pudo enviar el aviso por correo: {error}')
