from django.test import RequestFactory

from core.red import ip_cliente


def _peticion(remota='10.0.0.1', reenviada=None):
    extra = {'REMOTE_ADDR': remota}
    if reenviada is not None:
        extra['HTTP_X_FORWARDED_FOR'] = reenviada
    return RequestFactory().get('/', **extra)


def test_sin_proxies_usa_la_ip_de_la_conexion(settings):
    settings.NUM_PROXIES = 0

    # Un X-Forwarded-For escrito por el cliente no se toma en cuenta.
    assert ip_cliente(_peticion('192.168.1.5', '1.2.3.4')) == '192.168.1.5'


def test_detras_de_un_proxy_usa_la_ip_que_agrego_el_proxy(settings):
    settings.NUM_PROXIES = 1

    # El cliente intentó hacerse pasar por 1.1.1.1; el proxy agregó al final la real.
    assert ip_cliente(_peticion('10.0.0.1', '1.1.1.1, 200.10.20.30')) == '200.10.20.30'


def test_detras_de_dos_proxies_cuenta_dos_desde_el_final(settings):
    settings.NUM_PROXIES = 2

    assert ip_cliente(_peticion('10.0.0.1', '1.1.1.1, 200.10.20.30, 172.70.1.1')) == '200.10.20.30'


def test_con_proxy_pero_sin_cabecera_usa_la_ip_de_la_conexion(settings):
    settings.NUM_PROXIES = 1

    assert ip_cliente(_peticion('200.10.20.30')) == '200.10.20.30'


def test_una_ip_invalida_se_guarda_como_nula(settings):
    settings.NUM_PROXIES = 1

    assert ip_cliente(_peticion('10.0.0.1', 'no-es-ip')) is None


def test_acepta_ipv6(settings):
    settings.NUM_PROXIES = 1

    assert ip_cliente(_peticion('10.0.0.1', '2001:db8::1')) == '2001:db8::1'
