from django.db import models


class Categoria(models.Model):
    """Modelo mínimo — CRUD completo en la feature 007 · Catálogo."""

    nombre_categoria = models.CharField(max_length=100)
    descripcion_categoria = models.TextField(blank=True)
    activo_categoria = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'categorías'

    def __str__(self):
        return self.nombre_categoria


class Producto(models.Model):
    """Modelo mínimo — CRUD completo en la feature 007 · Catálogo. No
    incluye todavía todos los campos de Base de Datos FleboSil.txt (ej.
    fecha_registro), solo lo necesario para inventario/alertas.
    """

    nombre_producto = models.CharField(max_length=150)
    sku = models.CharField(max_length=50, unique=True)
    unidad_medida = models.CharField(max_length=30)
    descripcion_producto = models.TextField(blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='productos')
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    costo_produccion = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    activo_producto = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre_producto


class MateriaPrima(models.Model):
    """Modelo mínimo — CRUD completo en la feature 007 · Catálogo.
    `proveedor_principal` (FK → Proveedores, feature 008 · Personas) se
    agrega cuando esa feature exista.
    """

    nombre_item = models.CharField(max_length=150)
    unidad_medida = models.CharField(max_length=30)
    costo_promedio = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    activo_item = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'materias primas'

    def __str__(self):
        return self.nombre_item
