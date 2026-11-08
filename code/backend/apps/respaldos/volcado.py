"""`pg_dump` / `pg_restore` contra la base configurada en settings (023).

La contraseña de la base va por la variable `PGPASSWORD` del proceso hijo,
nunca en la línea de comandos (se vería en la lista de procesos).
"""

import os
import shutil
import subprocess

from django.conf import settings


class ErrorVolcado(Exception):
    """`pg_dump` o `pg_restore` terminó con error."""


def _ejecutable(nombre):
    carpeta = getattr(settings, 'RESPALDO_PG_BIN', '')
    if carpeta:
        for candidato in (nombre, f'{nombre}.exe'):
            ruta = os.path.join(carpeta, candidato)
            if os.path.isfile(ruta):
                return ruta
    ruta = shutil.which(nombre)
    if not ruta:
        raise ErrorVolcado(
            f'No se encontró {nombre}. Instala el cliente de PostgreSQL 16+ o indica su carpeta en PG_BIN.',
        )
    return ruta


def datos_conexion(base=None):
    bd = settings.DATABASES['default']
    return {
        'host': bd.get('HOST') or 'localhost',
        'puerto': str(bd.get('PORT') or '5432'),
        'usuario': bd.get('USER') or '',
        'base': base or bd['NAME'],
        'password': bd.get('PASSWORD') or '',
    }


def _ejecutar(argumentos, password):
    entorno = {**os.environ, 'PGPASSWORD': password, 'PGCONNECT_TIMEOUT': '30'}
    resultado = subprocess.run(argumentos, env=entorno, capture_output=True, text=True, check=False)
    if resultado.returncode != 0:
        detalle = (resultado.stderr or resultado.stdout).strip()[-1000:]
        raise ErrorVolcado(f'{os.path.basename(argumentos[0])} terminó con error: {detalle}')
    return resultado.stdout


def _conexion(c):
    return ['--host', c['host'], '--port', c['puerto'], '--username', c['usuario'], '--no-password']


def volcar_base(archivo_destino):
    """Volcado completo en formato personalizado (comprimido, restaurable por tabla)."""
    c = datos_conexion()
    _ejecutar(
        [_ejecutable('pg_dump'), *_conexion(c), '--format=custom', '--no-owner', '--no-privileges',
         '--file', str(archivo_destino), c['base']],
        c['password'],
    )


def verificar_volcado(archivo):
    """Comprueba que el volcado se puede leer; devuelve cuántas entradas trae."""
    salida = _ejecutar([_ejecutable('pg_restore'), '--list', str(archivo)], '')
    entradas = [linea for linea in salida.splitlines() if linea.strip() and not linea.startswith(';')]
    if not entradas:
        raise ErrorVolcado('El volcado está vacío.')
    return len(entradas)


def restaurar_volcado(archivo, base):
    c = datos_conexion(base)
    _ejecutar(
        [_ejecutable('pg_restore'), *_conexion(c), '--dbname', c['base'], '--no-owner', '--no-privileges',
         '--exit-on-error', str(archivo)],
        c['password'],
    )
