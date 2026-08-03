from django.db import models


class Sucursal(models.Model):
    """Modelo mínimo — el CRUD completo (views/serializers/permisos) se
    implementa en la feature 006 · Sucursales. Aquí solo lo necesario para
    que Inventario (009) y el endpoint de alertas de la feature 001 puedan
    referenciarlo por FK.
    """

    nombre_sucursal = models.CharField(max_length=150)
    ubicacion_sucursal = models.CharField(max_length=255, blank=True)
    telefono_sucursal = models.CharField(max_length=30, blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre_sucursal
