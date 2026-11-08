"""IP real del cliente detrás de los proxies de producción (022)."""

import ipaddress

from django.conf import settings


def _ip_valida(valor):
    try:
        return str(ipaddress.ip_address(valor.strip()))
    except ValueError:
        return None


def ip_cliente(request):
    """IP del cliente con el mismo criterio que el throttling de DRF.

    Detrás de Railway, `REMOTE_ADDR` es la IP del balanceador y la del cliente
    llega en `X-Forwarded-For`. Cada proxy agrega al final la IP de quien le
    habló, así que con `NUM_PROXIES = n` la IP confiable es la n-ésima desde
    el final: las de más a la izquierda las pudo escribir el propio cliente.
    Sin proxies configurados (local) se usa `REMOTE_ADDR`. Devuelve `None` si
    no hay una IP válida (el campo `RegistroAcceso.ip` admite nulos).
    """
    remota = request.META.get('REMOTE_ADDR', '')
    reenviada = request.META.get('HTTP_X_FORWARDED_FOR')
    num_proxies = getattr(settings, 'NUM_PROXIES', 0)
    if num_proxies and reenviada:
        direcciones = [d for d in reenviada.split(',') if d.strip()]
        if direcciones:
            return _ip_valida(direcciones[-min(num_proxies, len(direcciones))])
    return _ip_valida(remota) if remota else None
