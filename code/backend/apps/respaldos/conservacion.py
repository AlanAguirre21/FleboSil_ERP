"""Regla de conservación de respaldos (023).

Se conservan los 12 respaldos más recientes y, además, el primer respaldo de
cada uno de los 12 meses más recientes que tengan alguno. Todo lo demás se
puede borrar. Funciones puras: no tocan disco ni red.
"""

import re
from datetime import datetime
from zoneinfo import ZoneInfo

SEMANALES = 12
MENSUALES = 12

PREFIJO_NOMBRE = 'flebosil_'
EXTENSION = '.dump.cifrado'
# Los nombres llevan la hora local del negocio (como `TIME_ZONE`).
ZONA = ZoneInfo('America/Mexico_City')
_PATRON_NOMBRE = re.compile(r'^flebosil_(\d{4}-\d{2}-\d{2}_\d{4})\.dump\.cifrado$')


def nombre_respaldo(momento):
    """`flebosil_AAAA-MM-DD_HHMM.dump.cifrado`, con la hora local del negocio."""
    if momento.tzinfo is not None:
        momento = momento.astimezone(ZONA)
    return f'{PREFIJO_NOMBRE}{momento:%Y-%m-%d_%H%M}{EXTENSION}'


def fecha_de_nombre(nombre):
    """Fecha de un nombre de respaldo, o `None` si no es un respaldo nuestro
    (la regla nunca toca archivos que no siguen el patrón)."""
    coincidencia = _PATRON_NOMBRE.match(nombre)
    if not coincidencia:
        return None
    return datetime.strptime(coincidencia.group(1), '%Y-%m-%d_%H%M').replace(tzinfo=ZONA)


def nombres_a_conservar(nombres, semanales=SEMANALES, mensuales=MENSUALES):
    """De una lista de nombres de respaldo, los que entran en la regla."""
    fechados = sorted(
        ((fecha, nombre) for nombre in nombres if (fecha := fecha_de_nombre(nombre))),
        reverse=True,
    )
    conservar = {nombre for _, nombre in fechados[:semanales]}

    primero_del_mes = {}
    for fecha, nombre in fechados:  # del más reciente al más antiguo
        primero_del_mes[(fecha.year, fecha.month)] = nombre  # queda el más antiguo del mes
    for mes in sorted(primero_del_mes, reverse=True)[:mensuales]:
        conservar.add(primero_del_mes[mes])
    return conservar


def nombres_a_borrar(nombres, **kwargs):
    """Respaldos que ya no entran en la regla, del más antiguo al más reciente."""
    conservar = nombres_a_conservar(nombres, **kwargs)
    return sorted(
        (n for n in nombres if fecha_de_nombre(n) and n not in conservar),
        key=fecha_de_nombre,
    )
