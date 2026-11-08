"""Administrador protegido (feature 022): un único usuario de control que
siempre existe y cuyo correo, contraseña, rol y estado no se cambian desde
la app. Lo crea/restaura `manage.py asegurar_admin`.
"""

from django.conf import settings

MENSAJE_ADMIN_PROTEGIDO = (
    'El administrador de control no se puede modificar: su correo, contraseña, rol y estado son fijos.'
)


def es_admin_protegido(usuario):
    return bool(usuario and usuario.email and usuario.email.lower() == settings.ADMIN_PROTEGIDO_EMAIL)
