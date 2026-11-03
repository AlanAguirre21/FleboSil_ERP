from importlib import import_module

import pytest
from django.apps import apps as django_apps

SIEMBRAS_CATALOGO_DE_CUENTAS = [
    ('0002_cuentas_base', 'cargar_catalogo_base'),
    ('0003_cuenta_sueldos', 'crear_cuenta_sueldos'),
]


@pytest.fixture
def catalogo_de_cuentas(db):
    """Vuelve a sembrar el catálogo de cuentas de las migraciones de
    Contabilidad. Lo necesitan las pruebas `transaction=True`: al terminar,
    pytest-django vacía la base y con ella esos datos, que Ventas, Compras y
    Caja necesitan para generar sus asientos. Las funciones de siembra usan
    `get_or_create`, así que llamarlas de nuevo no duplica nada.
    """
    for migracion, funcion in SIEMBRAS_CATALOGO_DE_CUENTAS:
        modulo = import_module(f'apps.contabilidad.migrations.{migracion}')
        getattr(modulo, funcion)(django_apps, None)
