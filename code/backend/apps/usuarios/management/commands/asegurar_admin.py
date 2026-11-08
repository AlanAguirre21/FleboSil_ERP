"""Crea o restaura el administrador protegido — feature 022.

Corre en cada despliegue después de `migrate`. Es idempotente: si el
usuario ya está como debe, no cambia nada.
"""

import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.usuarios.models import Usuario
from core.permissions import ROL_ADMIN


class Command(BaseCommand):
    help = 'Crea o restaura el administrador protegido (correo fijo, contraseña de ADMIN_PASSWORD).'

    def handle(self, *args, **opciones):
        password = os.environ.get('ADMIN_PASSWORD', '')
        if not password:
            raise CommandError('Falta la variable de entorno ADMIN_PASSWORD.')

        email = settings.ADMIN_PROTEGIDO_EMAIL
        usuario = Usuario.objects.filter(email__iexact=email).first()
        creado = usuario is None
        if creado:
            username = 'Administrador'
            if Usuario.objects.filter(username__iexact=username).exists():
                username = email
            usuario = Usuario(email=email, username=username, first_name='Administrador')

        cambios = []
        for campo, valor in (('email', email), ('rol_usuario', ROL_ADMIN), ('is_active', True),
                             ('is_staff', True), ('is_superuser', True)):
            if getattr(usuario, campo) != valor:
                setattr(usuario, campo, valor)
                cambios.append(campo)
        if creado or not usuario.check_password(password):
            usuario.set_password(password)
            cambios.append('password')

        if cambios:
            usuario.save()
        if creado:
            self.stdout.write(self.style.SUCCESS(f'Administrador protegido creado: {email}'))
        elif cambios:
            self.stdout.write(self.style.WARNING(f'Administrador protegido restaurado ({", ".join(cambios)}).'))
        else:
            self.stdout.write(f'Administrador protegido sin cambios: {email}')
