import pytest
from django.core.exceptions import ImproperlyConfigured

from config.settings import _variable_obligatoria


def test_una_variable_obligatoria_faltante_impide_arrancar(monkeypatch):
    monkeypatch.delenv('VARIABLE_DE_PRUEBA', raising=False)

    with pytest.raises(ImproperlyConfigured, match='VARIABLE_DE_PRUEBA'):
        _variable_obligatoria('VARIABLE_DE_PRUEBA')


def test_una_variable_obligatoria_vacia_impide_arrancar(monkeypatch):
    monkeypatch.setenv('VARIABLE_DE_PRUEBA', '')

    with pytest.raises(ImproperlyConfigured):
        _variable_obligatoria('VARIABLE_DE_PRUEBA')


def test_una_variable_obligatoria_definida_se_usa(monkeypatch):
    monkeypatch.setenv('VARIABLE_DE_PRUEBA', 'valor')

    assert _variable_obligatoria('VARIABLE_DE_PRUEBA') == 'valor'
