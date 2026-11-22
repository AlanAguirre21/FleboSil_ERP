from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import es_admin

from .serializers import NotificacionesSerializer
from .services import armar_notificaciones


class NotificacionesView(APIView):
    """GET /api/notificaciones/ — secciones de la campana del Header y su
    contador (`001`, "Actualización: centro de notificaciones y avisos por
    correo"). El admin ve toda la empresa y las nóminas; el operador, solo
    sus ventas, compras y facturas, y el stock de toda la empresa.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        admin = es_admin(request.user)
        datos = armar_notificaciones(usuario=None if admin else request.user, incluir_nominas=admin)
        return Response(NotificacionesSerializer(datos).data)
