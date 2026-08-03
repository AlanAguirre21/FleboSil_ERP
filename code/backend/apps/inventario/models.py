from django.db import models

from apps.catalogo.models import MateriaPrima, Producto
from apps.sucursales.models import Sucursal


class InventarioSucursalProducto(models.Model):
    """Modelo mínimo — la feature 009 · Inventario agrega el resto
    (MovimientoInventario, historial, etc.). Aquí solo lo necesario para el
    endpoint de alertas de stock de la feature 001 · Header.
    """

    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE, related_name='inventario_productos')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='inventarios')
    stock_actual = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    stock_minimo = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        unique_together = ('sucursal', 'producto')

    def __str__(self):
        return f'{self.producto} @ {self.sucursal}'


class InventarioSucursalMateriaPrima(models.Model):
    """Modelo mínimo — ver nota en InventarioSucursalProducto."""

    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE, related_name='inventario_materia_prima')
    materia_prima = models.ForeignKey(MateriaPrima, on_delete=models.CASCADE, related_name='inventarios')
    stock_actual = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    stock_minimo = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        unique_together = ('sucursal', 'materia_prima')

    def __str__(self):
        return f'{self.materia_prima} @ {self.sucursal}'
