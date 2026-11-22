"""Envía el resumen diario de pendientes a los admins (`001`, "Actualización:
centro de notificaciones y avisos por correo").

En producción lo corre un servicio cron de Railway a las 02:00 UTC (20:00 de
Ciudad de México, sin horario de verano). `--para` lo envía solo a esos
correos, para probarlo sin escribir a los admins.
"""

from django.core.management.base import BaseCommand

from apps.notificaciones.correo import enviar_resumen_diario


class Command(BaseCommand):
    help = 'Envía por correo el resumen diario de pendientes a los admins.'

    def add_arguments(self, parser):
        parser.add_argument('--para', nargs='+', help='Correos de prueba (en lugar de los admins).')

    def handle(self, *args, **opciones):
        enviados = enviar_resumen_diario(para=opciones.get('para'))
        if enviados:
            self.stdout.write(self.style.SUCCESS(f'Resumen diario enviado ({enviados} correo(s)).'))
        else:
            self.stdout.write('Sin pendientes que reportar o sin destinatarios: no se envió el resumen.')
