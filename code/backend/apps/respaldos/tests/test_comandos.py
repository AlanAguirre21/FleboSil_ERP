"""Comandos de respaldo con `pg_dump`/`pg_restore` simulados (sin base real)."""

import io
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from django.core import mail
from django.core.management import CommandError, call_command

from apps.respaldos import cifrado
from apps.respaldos.almacenes import AlmacenLocal
from apps.respaldos.cifrado import cifrar_archivo, descifrar_archivo
from apps.respaldos.conservacion import ZONA, nombre_respaldo, nombres_a_conservar
from apps.respaldos.management.commands import respaldar as modulo_respaldar
from apps.respaldos.management.commands import restaurar_respaldo as modulo_restaurar
from apps.respaldos.volcado import ErrorVolcado

VOLCADO_FALSO = b'PGDMP volcado de prueba ' * 100


@pytest.fixture(autouse=True)
def scrypt_rapido(monkeypatch):
    monkeypatch.setattr(cifrado, 'LOG2_N_SCRYPT', 10)


@pytest.fixture
def pg_falso(monkeypatch):
    """`pg_dump` escribe un volcado falso; `pg_restore --list` lo da por bueno."""
    llamadas = []

    def volcar(destino):
        llamadas.append('volcar')
        with open(destino, 'wb') as archivo:
            archivo.write(VOLCADO_FALSO)

    monkeypatch.setattr(modulo_respaldar, 'volcar_base', volcar)
    monkeypatch.setattr(modulo_respaldar, 'verificar_volcado', lambda archivo: 42)
    return llamadas


@pytest.fixture
def carpeta(settings, tmp_path):
    settings.RESPALDO_CARPETA = str(tmp_path / 'respaldos')
    return tmp_path / 'respaldos'


def _respaldar(destino='local'):
    salida, errores = io.StringIO(), io.StringIO()
    call_command('respaldar', destino=destino, stdout=salida, stderr=errores)
    return salida.getvalue() + errores.getvalue()


def _viejos(carpeta, cuantos):
    """Respaldos anteriores, uno por domingo desde enero de 2025."""
    (carpeta / 'base').mkdir(parents=True, exist_ok=True)
    nombres = [nombre_respaldo(datetime(2025, 1, 5, 3, 0, tzinfo=ZONA) + timedelta(weeks=i)) for i in range(cuantos)]
    for nombre in nombres:
        (carpeta / 'base' / nombre).write_bytes(b'viejo')
    return nombres


def test_guarda_el_volcado_cifrado_y_se_puede_descifrar(pg_falso, carpeta, password_respaldo, tmp_path):
    salida = _respaldar()

    [respaldo] = (carpeta / 'base').iterdir()
    assert respaldo.name.startswith('flebosil_') and respaldo.name.endswith('.dump.cifrado')
    assert b'PGDMP' not in respaldo.read_bytes()
    descifrar_archivo(respaldo, tmp_path / 'vuelta.dump', password_respaldo)
    assert (tmp_path / 'vuelta.dump').read_bytes() == VOLCADO_FALSO
    assert 'Respaldo guardado' in salida and '42 objetos' in salida


def test_aplica_la_conservacion_despues_de_guardar(pg_falso, carpeta, password_respaldo):
    _viejos(carpeta, 40)
    (carpeta / 'base' / 'notas.txt').write_text('no tocar')

    salida = _respaldar()

    restantes = sorted(a.name for a in (carpeta / 'base').iterdir())
    assert 'notas.txt' in restantes
    respaldos = [n for n in restantes if n.endswith('.dump.cifrado')]
    # Lo que queda es exactamente lo que pide la regla, incluido el nuevo.
    assert set(respaldos) == nombres_a_conservar(respaldos)
    assert len(respaldos) < 41
    assert any(n.startswith('flebosil_2025-01-05') for n in respaldos)  # primero de enero 2025
    assert 'Borrados por antigüedad' in salida


def test_en_r2(pg_falso, password_respaldo, monkeypatch, r2, cliente_r2):
    monkeypatch.setattr(modulo_respaldar, 'almacen', lambda destino: r2)

    _respaldar('r2')

    [clave] = cliente_r2.objetos
    assert clave.startswith('base/flebosil_')
    assert b'PGDMP' not in cliente_r2.objetos[clave]


def test_ante_un_fallo_no_borra_nada_y_avisa_por_correo(monkeypatch, carpeta, password_respaldo, settings):
    settings.RESPALDO_AVISO_EMAIL = 'admin@flebosil.com'
    viejos = _viejos(carpeta, 30)

    def falla(destino):
        raise ErrorVolcado('pg_dump terminó con error: could not connect to server')

    monkeypatch.setattr(modulo_respaldar, 'volcar_base', falla)

    with pytest.raises(CommandError, match='could not connect'):
        _respaldar()

    assert sorted(a.name for a in (carpeta / 'base').iterdir()) == sorted(viejos)
    [aviso] = mail.outbox
    assert aviso.to == ['admin@flebosil.com']
    assert 'Falló el respaldo' in aviso.subject
    assert 'could not connect' in aviso.body


def test_sin_contrasena_falla_sin_respaldar(pg_falso, carpeta, settings):
    settings.RESPALDO_PASSWORD = ''

    with pytest.raises(CommandError, match='RESPALDO_PASSWORD'):
        _respaldar()
    assert pg_falso == []


def test_sin_carpeta_local_falla(pg_falso, settings, password_respaldo):
    settings.RESPALDO_CARPETA = ''

    with pytest.raises(CommandError, match='RESPALDO_CARPETA'):
        _respaldar()


def test_nunca_imprime_secretos(pg_falso, carpeta, password_respaldo, monkeypatch):
    conexion = {'host': 'db.ejemplo', 'puerto': '5432', 'usuario': 'u', 'base': 'b', 'password': 'clave-de-la-base-999'}
    monkeypatch.setattr(modulo_respaldar, 'datos_conexion', lambda: conexion)

    salida = _respaldar()

    assert password_respaldo not in salida
    assert 'clave-de-la-base-999' not in salida


# --- restaurar y descifrar -------------------------------------------------


def _respaldo_cifrado(tmp_path, password):
    plano = tmp_path / 'plano.dump'
    plano.write_bytes(VOLCADO_FALSO)
    destino = tmp_path / 'flebosil_2026-11-08_0300.dump.cifrado'
    cifrar_archivo(plano, destino, password)
    return destino


def test_restaurar_descifra_y_restaura_en_la_base_vacia(monkeypatch, tmp_path, password_respaldo):
    restaurado = {}

    def restaurar(archivo, base):
        restaurado['contenido'] = Path(archivo).read_bytes()
        restaurado['base'] = base

    monkeypatch.setattr(modulo_restaurar, 'tablas_en_base', lambda base: 0)
    monkeypatch.setattr(modulo_restaurar, 'verificar_volcado', lambda archivo: 42)
    monkeypatch.setattr(modulo_restaurar, 'restaurar_volcado', restaurar)

    call_command('restaurar_respaldo', str(_respaldo_cifrado(tmp_path, password_respaldo)),
                 base='flebosil_prueba', noinput=True, stdout=io.StringIO())

    assert restaurado == {'contenido': VOLCADO_FALSO, 'base': 'flebosil_prueba'}


def test_restaurar_se_niega_si_la_base_tiene_tablas(monkeypatch, tmp_path, password_respaldo):
    monkeypatch.setattr(modulo_restaurar, 'tablas_en_base', lambda base: 80)
    monkeypatch.setattr(modulo_restaurar, 'restaurar_volcado', lambda *a: pytest.fail('no debía restaurar'))

    with pytest.raises(CommandError, match='no está vacía'):
        call_command('restaurar_respaldo', str(_respaldo_cifrado(tmp_path, password_respaldo)),
                     base='flebosil_db', noinput=True)


def test_restaurar_con_otra_contrasena_no_toca_la_base(monkeypatch, tmp_path, password_respaldo, settings):
    archivo = _respaldo_cifrado(tmp_path, password_respaldo)
    settings.RESPALDO_PASSWORD = 'otra'
    monkeypatch.setattr(modulo_restaurar, 'tablas_en_base', lambda base: 0)
    monkeypatch.setattr(modulo_restaurar, 'restaurar_volcado', lambda *a: pytest.fail('no debía restaurar'))

    with pytest.raises(CommandError, match='contraseña es incorrecta'):
        call_command('restaurar_respaldo', str(archivo), base='flebosil_prueba', noinput=True)


def test_restaurar_pide_confirmacion(monkeypatch, tmp_path, password_respaldo):
    monkeypatch.setattr(modulo_restaurar, 'tablas_en_base', lambda base: 0)
    monkeypatch.setattr(modulo_restaurar, 'restaurar_volcado', lambda *a: pytest.fail('no debía restaurar'))
    monkeypatch.setattr('builtins.input', lambda texto: 'n')

    with pytest.raises(CommandError, match='Cancelado'):
        call_command('restaurar_respaldo', str(_respaldo_cifrado(tmp_path, password_respaldo)), base='x')


def test_descifrar_respaldo(tmp_path, password_respaldo):
    salida = tmp_path / 'descifrado.dump'

    call_command('descifrar_respaldo', str(_respaldo_cifrado(tmp_path, password_respaldo)),
                 salida=str(salida), stdout=io.StringIO())

    assert salida.read_bytes() == VOLCADO_FALSO


def test_descifrar_no_sobrescribe(tmp_path, password_respaldo):
    salida = tmp_path / 'ya_existe.dump'
    salida.write_bytes(b'importante')

    with pytest.raises(CommandError, match='Ya existe'):
        call_command('descifrar_respaldo', str(_respaldo_cifrado(tmp_path, password_respaldo)), salida=str(salida))
    assert salida.read_bytes() == b'importante'


def test_almacen_local_no_sale_de_su_carpeta(tmp_path):
    with pytest.raises(ValueError):
        AlmacenLocal(tmp_path / 'respaldos').guardar_bytes(b'x', '../fuera.txt')
