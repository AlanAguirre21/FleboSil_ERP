from django.contrib.auth.models import AbstractUser
from django.db import models

from core.permissions import ROL_ADMIN, ROL_OPERADOR

ROLES_USUARIO = [
    (ROL_ADMIN, 'Administrador'),
    (ROL_OPERADOR, 'Operador'),
]


class Usuario(AbstractUser):
    """Modelo de usuario autenticado. Campos adicionales (empleado, foto,
    etc. — ver Base de Datos FleboSil.txt) se agregan en la feature 008
    · Personas, que es dueña del CRUD completo de este modelo.
    """

    email = models.EmailField('correo electrónico', unique=True)
    rol_usuario = models.CharField(max_length=20, choices=ROLES_USUARIO, default=ROL_OPERADOR)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def nombre_mostrado(self):
        return self.get_full_name() or self.username
