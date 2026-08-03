from django.urls import path

from .views import AlertasStockView

urlpatterns = [
    path('alertas/', AlertasStockView.as_view(), name='inventario-alertas'),
]
