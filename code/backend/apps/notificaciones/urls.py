from django.urls import path

from .views import NotificacionesView

urlpatterns = [
    path('', NotificacionesView.as_view(), name='notificaciones'),
]
