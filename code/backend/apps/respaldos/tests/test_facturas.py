"""Copia de las facturas en R2 (023), con un bucket en memoria."""

import io

import pytest
from django.core.management import call_command

from apps.facturacion.views import _guardar_archivo_factura
from apps.respaldos import cifrado, facturas
from apps.respaldos.almacenes import AlmacenLocal
from apps.respaldos.cifrado import descifrar_flujo


@pytest.fixture(autouse=True)
def entorno(settings, tmp_path, monkeypatch, r2, password_respaldo):
    monkeypatch.setattr(cifrado, 'LOG2_N_SCRYPT', 10)
    settings.MEDIA_ROOT = str(tmp_path / 'media')
    settings.R2_ENDPOINT = 'https://r2.ejemplo'
    settings.R2_BUCKET = 'flebosil-respaldos'
    settings.R2_ACCESS_KEY_ID = 'id'
    settings.R2_SECRET_ACCESS_KEY = 'secreto'
    monkeypatch.setattr(facturas, 'almacen_r2', lambda: r2)
    monkeypatch.setattr('apps.respaldos.management.commands.subir_facturas_pendientes.almacen_r2', lambda: r2)


def _descifrado(datos):
    salida = io.BytesIO()
    descifrar_flujo(io.BytesIO(datos), salida, 'contraseña-de-prueba-123')
    return salida.getvalue()


@pytest.mark.django_db
def test_al_guardar_una_factura_se_sube_cifrada_al_confirmar(cliente_r2, django_capture_on_commit_callbacks):
    with django_capture_on_commit_callbacks(execute=True):
        ruta = _guardar_archivo_factura('15.xml', b'<cfdi:Comprobante Total="100"/>')

    assert ruta.replace('\\', '/') == 'facturas/15.xml'
    datos = cliente_r2.objetos['facturas/15.xml.cifrado']
    assert b'Comprobante' not in datos
    assert _descifrado(datos) == b'<cfdi:Comprobante Total="100"/>'


@pytest.mark.django_db
def test_si_la_transaccion_se_revierte_no_se_sube(cliente_r2, django_capture_on_commit_callbacks):
    with django_capture_on_commit_callbacks(execute=False) as pendientes:
        _guardar_archivo_factura('16.xml', b'<cfdi/>')

    assert len(pendientes) == 1  # solo correría al confirmar
    assert cliente_r2.objetos == {}


def test_un_fallo_de_r2_no_interrumpe_el_timbrado(monkeypatch, settings, tmp_path, caplog):
    (tmp_path / 'media' / 'facturas').mkdir(parents=True)
    (tmp_path / 'media' / 'facturas' / '17.xml').write_bytes(b'<cfdi/>')

    def falla():
        raise ConnectionError('R2 no responde')

    monkeypatch.setattr(facturas, 'almacen_r2', falla)

    facturas.respaldar_factura('facturas/17.xml')  # no lanza

    assert 'se reintentará al arrancar' in caplog.text


def test_sin_r2_no_hace_nada(settings, monkeypatch):
    settings.R2_BUCKET = ''
    monkeypatch.setattr(facturas, 'almacen_r2', lambda: pytest.fail('no debía usar R2'))

    facturas.respaldar_factura('facturas/1.xml')


def test_subir_pendientes_sube_solo_las_que_faltan(cliente_r2, tmp_path):
    carpeta = tmp_path / 'media' / 'facturas'
    carpeta.mkdir(parents=True)
    for nombre in ('1.xml', '1.pdf', '2.xml'):
        (carpeta / nombre).write_bytes(nombre.encode())
    cliente_r2.objetos['facturas/1.xml.cifrado'] = b'ya estaba'

    salida = io.StringIO()
    call_command('subir_facturas_pendientes', stdout=salida)

    assert cliente_r2.objetos['facturas/1.xml.cifrado'] == b'ya estaba'
    assert _descifrado(cliente_r2.objetos['facturas/1.pdf.cifrado']) == b'1.pdf'
    assert _descifrado(cliente_r2.objetos['facturas/2.xml.cifrado']) == b'2.xml'
    assert 'Facturas subidas a R2: 2.' in salida.getvalue()


def test_subir_pendientes_nunca_falla_el_arranque(monkeypatch):
    def falla():
        raise ConnectionError('R2 no responde')

    monkeypatch.setattr('apps.respaldos.management.commands.subir_facturas_pendientes.almacen_r2', falla)

    errores = io.StringIO()
    call_command('subir_facturas_pendientes', stdout=io.StringIO(), stderr=errores)

    assert 'R2 no responde' in errores.getvalue()


def test_descargar_copia_las_que_faltan_sin_descifrar(cliente_r2, settings, tmp_path, monkeypatch):
    settings.RESPALDO_CARPETA = str(tmp_path / 'respaldos')
    cliente_r2.objetos['facturas/1.xml.cifrado'] = b'cifrado-1'
    cliente_r2.objetos['facturas/2.pdf.cifrado'] = b'cifrado-2'
    cliente_r2.objetos['base/flebosil_2026-11-08_0300.dump.cifrado'] = b'no es factura'
    local = AlmacenLocal(tmp_path / 'respaldos')
    local.guardar_bytes(b'ya estaba', 'facturas/1.xml.cifrado')

    salida = io.StringIO()
    call_command('subir_facturas_pendientes', descargar=True, stdout=salida)

    assert (tmp_path / 'respaldos' / 'facturas' / '1.xml.cifrado').read_bytes() == b'ya estaba'
    assert (tmp_path / 'respaldos' / 'facturas' / '2.pdf.cifrado').read_bytes() == b'cifrado-2'
    assert not (tmp_path / 'respaldos' / 'base').exists()
    assert 'Facturas descargadas de R2: 1.' in salida.getvalue()
