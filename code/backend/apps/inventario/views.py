from django.db.models import F
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from .models import InventarioSucursalMateriaPrima, InventarioSucursalProducto
from .serializers import AlertaStockSerializer


class AlertasStockView(ListAPIView):
    """GET /api/inventario/alertas/ — productos y materia prima con
    stock_actual por debajo de stock_minimo, en cualquier sucursal.
    """

    serializer_class = AlertaStockSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        alertas_producto = InventarioSucursalProducto.objects.select_related(
            'producto', 'sucursal'
        ).filter(stock_actual__lt=F('stock_minimo'))

        alertas_materia_prima = InventarioSucursalMateriaPrima.objects.select_related(
            'materia_prima', 'sucursal'
        ).filter(stock_actual__lt=F('stock_minimo'))

        alertas = [
            {
                'tipo': 'producto',
                'nombre': item.producto.nombre_producto,
                'sucursal': item.sucursal.nombre_sucursal,
                'stock_actual': item.stock_actual,
                'stock_minimo': item.stock_minimo,
            }
            for item in alertas_producto
        ] + [
            {
                'tipo': 'materia_prima',
                'nombre': item.materia_prima.nombre_item,
                'sucursal': item.sucursal.nombre_sucursal,
                'stock_actual': item.stock_actual,
                'stock_minimo': item.stock_minimo,
            }
            for item in alertas_materia_prima
        ]
        return alertas
