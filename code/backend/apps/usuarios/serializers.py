from rest_framework import serializers

from core.modules import modulos_para_rol


class UsuarioActualSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nombre = serializers.SerializerMethodField()
    rol = serializers.CharField(source='rol_usuario')
    modulos = serializers.SerializerMethodField()

    def get_nombre(self, usuario):
        return usuario.nombre_mostrado()

    def get_modulos(self, usuario):
        return modulos_para_rol(usuario.rol_usuario)
