from django.apps import AppConfig


class RespaldosConfig(AppConfig):
    """023 · Respaldos: sin modelos, solo comandos y utilidades para respaldar
    la base de datos y las facturas, cifradas, en R2 y en el equipo local."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.respaldos'
    label = 'respaldos'
