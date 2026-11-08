from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario
from .protegido import es_admin_protegido


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """El administrador protegido (022) no se edita ni se borra desde aquí:
    el admin de Django escribe directo al modelo, sin los serializers."""

    def has_change_permission(self, request, obj=None):
        if es_admin_protegido(obj):
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if es_admin_protegido(obj):
            return False
        return super().has_delete_permission(request, obj)
