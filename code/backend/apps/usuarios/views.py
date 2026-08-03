from rest_framework.generics import GenericAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle

from .serializers import (
    LoginSerializer,
    SolicitarRecuperacionSerializer,
    UsuarioActualSerializer,
    VerificarCodigoSerializer,
)
from .throttling import ThrottleRecuperarPassword, ThrottleVerificarCodigo


class MeView(RetrieveAPIView):
    serializer_class = UsuarioActualSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class LoginView(GenericAPIView):
    """POST /api/auth/login/ — credenciales -> par de tokens JWT.

    Limitado por throttling (scope 'login') para mitigar fuerza bruta.
    """

    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'login'

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)


MENSAJE_RECUPERACION_ENVIADA = 'Si el correo está registrado, te enviamos un código de verificación.'


class SolicitarRecuperacionView(GenericAPIView):
    """POST /api/auth/recuperar/ — genera y envía un código de 6 dígitos.

    Responde siempre el mismo mensaje, exista o no el correo. También sirve
    para "reenviar", ya que cada llamada invalida el código anterior.
    """

    serializer_class = SolicitarRecuperacionSerializer
    permission_classes = [AllowAny]
    throttle_classes = [ThrottleRecuperarPassword]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.guardar()
        return Response({'detail': MENSAJE_RECUPERACION_ENVIADA})


class VerificarCodigoView(GenericAPIView):
    """POST /api/auth/verificar-codigo/ — valida el código de 6 dígitos."""

    serializer_class = VerificarCodigoSerializer
    permission_classes = [AllowAny]
    throttle_classes = [ThrottleVerificarCodigo]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.guardar()
        return Response({'detail': 'Código verificado correctamente.'})
