"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""
import re

from django.conf import settings
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path, re_path
from django.views.static import serve
from rest_framework_simplejwt.views import TokenRefreshView

from apps.usuarios.views import (
    CambiarContrasenaView,
    LoginView,
    LogoutView,
    SolicitarRecuperacionView,
    VerificarCodigoView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/login/', LoginView.as_view(), name='auth-login'),
    path('api/auth/logout/', LogoutView.as_view(), name='auth-logout'),
    path('api/auth/recuperar/', SolicitarRecuperacionView.as_view(), name='auth-recuperar'),
    path(
        'api/auth/verificar-codigo/',
        VerificarCodigoView.as_view(),
        name='auth-verificar-codigo',
    ),
    path(
        'api/auth/cambiar-contrasena/',
        CambiarContrasenaView.as_view(),
        name='auth-cambiar-contrasena',
    ),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('api/usuarios/', include('apps.usuarios.urls')),
    path('api/inventario/', include('apps.inventario.urls')),
    path('api/sucursales/', include('apps.sucursales.urls')),
    path('api/catalogo/', include('apps.catalogo.urls')),
    path('api/terceros/', include('apps.terceros.urls')),
    path('api/rrhh/', include('apps.rrhh.urls')),
    path('api/compras/', include('apps.compras.urls')),
    path('api/ventas/', include('apps.ventas.urls')),
    path('api/produccion/', include('apps.produccion.urls')),
    path('api/caja/', include('apps.caja.urls')),
    path('api/reportes/', include('apps.reportes.urls')),
    path('api/configuracion-fiscal/', include('apps.configuracion_fiscal.urls')),
    path('api/facturacion/', include('apps.facturacion.urls')),
    path('api/contabilidad/', include('apps.contabilidad.urls')),
]


def salud(request):
    """GET /salud/ — revisión de salud de Railway: responde sin tocar la base
    ni pedir sesión, para saber que Gunicorn ya atiende antes de enviarle
    tráfico en cada despliegue."""
    return JsonResponse({'estado': 'ok'})


def _servir_fotos(prefijo, nombre_carpeta):
    """Sirve una carpeta de fotos por URL, también en producción (022): sin
    Nginx no hay otro servidor de archivos y el tráfico es bajo. Solo las
    fotografías de empleado (008 · RRHH) y de perfil de usuario (017 / 010) —
    nunca `MEDIA_URL`/`MEDIA_ROOT`, que guardan los XML/PDF de Facturación y
    deben seguir sin una URL pública (ver nota en `config/settings.py`).
    `serve` ya impide salir de la carpeta (`..`) y no lista directorios. La
    carpeta se lee de settings en cada petición, no al importar este módulo."""

    def vista(request, path):
        return serve(request, path, document_root=getattr(settings, nombre_carpeta))

    return re_path(rf'^{re.escape(prefijo.lstrip("/"))}(?P<path>.*)$', vista)


urlpatterns += [
    path('salud/', salud, name='salud'),
    _servir_fotos(settings.EMPLEADOS_FOTOS_URL, 'EMPLEADOS_FOTOS_ROOT'),
    _servir_fotos(settings.USUARIOS_FOTOS_URL, 'USUARIOS_FOTOS_ROOT'),
]

# Errores fuera de DRF también en JSON `{"detail": ...}` (022).
handler404 = 'core.excepciones.no_encontrado'
handler500 = 'core.excepciones.error_servidor'
