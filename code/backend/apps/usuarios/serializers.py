import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken

from core.modules import modulos_para_rol

from .models import CodigoRecuperacion

Usuario = get_user_model()

VIGENCIA_CODIGO_MINUTOS = 10


class UsuarioActualSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nombre = serializers.SerializerMethodField()
    rol = serializers.CharField(source='rol_usuario')
    modulos = serializers.SerializerMethodField()

    def get_nombre(self, usuario):
        return usuario.nombre_mostrado()

    def get_modulos(self, usuario):
        return modulos_para_rol(usuario.rol_usuario)


class LoginSerializer(serializers.Serializer):
    """Valida credenciales y emite el par de tokens JWT.

    No reutiliza `authenticate()`/`TokenObtainPairSerializer` porque ambos
    fallan de forma indistinguible ante contraseña incorrecta o cuenta
    inactiva; el criterio de aceptación exige mensajes distintos para cada
    caso (genérico para credenciales, específico para cuenta inactiva).
    """

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        usuario = Usuario.objects.filter(email=attrs['email']).first()

        if usuario is None or not usuario.check_password(attrs['password']):
            raise AuthenticationFailed('Correo o contraseña incorrectos.')

        if not usuario.is_active:
            raise AuthenticationFailed('Tu cuenta está inactiva. Contacta a un administrador.')

        refresh = RefreshToken.for_user(usuario)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }


class SolicitarRecuperacionSerializer(serializers.Serializer):
    """Genera y envía un código nuevo; la vista siempre responde el mismo
    mensaje de éxito, exista o no el correo, para no permitir enumeración
    de usuarios registrados.
    """

    email = serializers.EmailField()

    def guardar(self):
        email = self.validated_data['email']
        usuario = Usuario.objects.filter(email=email, is_active=True).first()

        if usuario is None:
            return

        CodigoRecuperacion.objects.filter(usuario=usuario, usado=False).update(usado=True)

        codigo = f'{secrets.randbelow(1_000_000):06d}'
        CodigoRecuperacion.objects.create(
            usuario=usuario,
            codigo=codigo,
            expira_en=timezone.now() + timedelta(minutes=VIGENCIA_CODIGO_MINUTOS),
        )

        send_mail(
            subject='Código de recuperación de contraseña — FleboSil',
            message=(
                f'Tu código de recuperación es: {codigo}\n'
                f'Vence en {VIGENCIA_CODIGO_MINUTOS} minutos. '
                'Si no solicitaste este código, ignora este correo.'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )


class VerificarCodigoSerializer(serializers.Serializer):
    email = serializers.EmailField()
    codigo = serializers.CharField(min_length=6, max_length=6)

    def validate(self, attrs):
        registro = (
            CodigoRecuperacion.objects.filter(
                usuario__email=attrs['email'], codigo=attrs['codigo'], usado=False,
            )
            .order_by('-creado_en')
            .first()
        )

        if registro is None or not registro.vigente():
            raise AuthenticationFailed('Código inválido o expirado.')

        attrs['registro'] = registro
        return attrs

    def guardar(self):
        registro = self.validated_data['registro']
        registro.verificado = True
        registro.save(update_fields=['verificado'])
