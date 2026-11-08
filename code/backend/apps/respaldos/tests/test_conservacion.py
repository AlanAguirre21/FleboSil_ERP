from datetime import datetime, timedelta

from apps.respaldos.conservacion import (
    ZONA,
    fecha_de_nombre,
    nombre_respaldo,
    nombres_a_borrar,
    nombres_a_conservar,
)


def _domingos(cuantos, desde=datetime(2026, 1, 4, 3, 0, tzinfo=ZONA)):
    """Nombres de respaldos de `cuantos` domingos seguidos."""
    return [nombre_respaldo(desde + timedelta(weeks=i)) for i in range(cuantos)]


def test_nombre_y_fecha():
    nombre = nombre_respaldo(datetime(2026, 11, 8, 3, 0, tzinfo=ZONA))

    assert nombre == 'flebosil_2026-11-08_0300.dump.cifrado'
    assert fecha_de_nombre(nombre) == datetime(2026, 11, 8, 3, 0, tzinfo=ZONA)


def test_otros_archivos_no_cuentan_ni_se_borran():
    nombres = [*_domingos(30), 'notas.txt', 'flebosil_mal.dump.cifrado', 'flebosil_2026-01-04_0300.dump']

    borrar = nombres_a_borrar(nombres)

    assert 'notas.txt' not in borrar
    assert 'flebosil_mal.dump.cifrado' not in borrar
    assert 'flebosil_2026-01-04_0300.dump' not in borrar


def test_con_menos_de_12_no_se_borra_nada():
    assert nombres_a_borrar(_domingos(5)) == []


def test_con_exactamente_12_no_se_borra_nada():
    assert nombres_a_borrar(_domingos(12)) == []


def test_en_la_semana_13_el_mas_viejo_se_queda_si_es_el_primero_de_su_mes():
    nombres = _domingos(13)  # 4 ene … 29 mar 2026

    # El más viejo (4 de enero) es el primero de enero: se conserva como mensual.
    assert nombres_a_borrar(nombres) == []


def test_en_la_semana_14_se_borra_el_segundo_de_enero():
    nombres = _domingos(14)

    assert nombres_a_borrar(nombres) == ['flebosil_2026-01-11_0300.dump.cifrado']


def test_regimen_estable_12_semanales_mas_el_primero_de_12_meses():
    nombres = _domingos(104)  # dos años de domingos
    fechas = sorted(fecha_de_nombre(n) for n in nombres)

    conservar = {fecha_de_nombre(n) for n in nombres_a_conservar(nombres)}

    semanales = set(fechas[-12:])
    meses = sorted({(f.year, f.month) for f in fechas})[-12:]
    primeros = {min(f for f in fechas if (f.year, f.month) == mes) for mes in meses}
    assert conservar == semanales | primeros
    assert 20 <= len(conservar) <= 24


def test_el_mes_13_se_borra():
    nombres = _domingos(70)
    conservar = nombres_a_conservar(nombres)
    meses_conservados = sorted({(fecha_de_nombre(n).year, fecha_de_nombre(n).month) for n in conservar})

    assert len(meses_conservados) == 12
    primero = fecha_de_nombre(min(nombres, key=fecha_de_nombre))
    assert (primero.year, primero.month) not in meses_conservados


def test_con_huecos_se_conservan_los_12_mas_recientes_que_existan():
    # El equipo estuvo apagado: respaldos sueltos en 2025 y 2026.
    nombres = [nombre_respaldo(datetime(2025, m, 1, 3, 0, tzinfo=ZONA)) for m in range(1, 13)]
    nombres += [nombre_respaldo(datetime(2026, 6, d, 3, 0, tzinfo=ZONA)) for d in (7, 14)]

    conservar = nombres_a_conservar(nombres)

    assert set(nombres[-12:]) <= conservar
    assert nombre_respaldo(datetime(2026, 6, 7, 3, 0, tzinfo=ZONA)) in conservar
    assert len(nombres_a_borrar(nombres)) == len(nombres) - len(conservar)


def test_borrar_va_del_mas_viejo_al_mas_nuevo():
    borrar = nombres_a_borrar(_domingos(60))

    assert borrar == sorted(borrar, key=fecha_de_nombre)
