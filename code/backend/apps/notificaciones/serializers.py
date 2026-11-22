from rest_framework import serializers


class ElementoNotificacionSerializer(serializers.Serializer):
    titulo = serializers.CharField()
    detalle = serializers.CharField()
    # "Vencida · hace N días", "Error de timbrado", "Por cobrar $X"…; o `null`.
    etiqueta = serializers.CharField(allow_null=True)
    urgente = serializers.BooleanField()
    ruta = serializers.CharField()


class SeccionNotificacionSerializer(serializers.Serializer):
    clave = serializers.CharField()
    titulo = serializers.CharField()
    ruta = serializers.CharField()
    total = serializers.IntegerField()
    requieren_accion = serializers.IntegerField()
    elementos = ElementoNotificacionSerializer(many=True)


class NotificacionesSerializer(serializers.Serializer):
    contador = serializers.IntegerField()
    secciones = SeccionNotificacionSerializer(many=True)
