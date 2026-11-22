from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import EsAdmin, es_admin

from .serializers import (
    ClienteTopOperadorSerializer,
    ClienteTopSerializer,
    MovimientoCajaReporteSerializer,
    ParametrosPeriodoSerializer,
    ProductoTopImporteSerializer,
    ProductoTopSerializer,
    ResumenComprasSerializer,
    ResumenDashboardOperadorSerializer,
    ResumenDashboardSerializer,
    ResumenFacturacionSerializer,
    ResumenProduccionOperadorSerializer,
    ResumenProduccionSerializer,
    ResumenVentasSerializer,
)
from .services import (
    LIMITE_10,
    LIMITES_VALIDOS,
    ORDEN_MAS,
    ORDENES_VALIDOS,
    TOP_CLIENTES_POR_COMPRAS,
    TOP_CLIENTES_POR_MONTO,
    TOP_PRODUCTOS_POR_CANTIDAD,
    TOP_PRODUCTOS_POR_IMPORTE,
    TOP_PRODUCTOS_POR_VALIDOS,
    calcular_resumen,
    calcular_resumen_compras,
    calcular_resumen_facturacion,
    calcular_resumen_produccion,
    calcular_resumen_ventas,
    calcular_top_clientes,
    calcular_top_productos,
    obtener_movimientos_caja,
    resolver_rango,
)


def _es_admin(request):
    return es_admin(request.user)


def _alcance(request):
    """`None` (toda la empresa) para el admin; el propio usuario para el
    operador, que solo ve cifras de sus ventas, compras y facturas (`016`,
    "Actualización: cifras propias para el operador")."""
    return None if _es_admin(request) else request.user


def _rango_de(request):
    """Valida `periodo`/`desde`/`hasta` con `ParametrosPeriodoSerializer`
    (400 si son inválidos; 403 si el operador pide algo distinto de "Día")
    y devuelve el `Rango` resuelto."""

    parametros = ParametrosPeriodoSerializer(data=request.query_params, context={'request': request})
    parametros.is_valid(raise_exception=True)
    datos = parametros.validated_data
    return resolver_rango(datos['periodo'], datos.get('desde'), datos.get('hasta'))


def _validar_orden(request):
    orden = request.query_params.get('orden', ORDEN_MAS)
    if orden not in ORDENES_VALIDOS:
        raise ValidationError({'orden': f'Debe ser uno de: {", ".join(ORDENES_VALIDOS)}.'})
    return orden


class ResumenDashboardView(APIView):
    """GET /api/reportes/resumen/?periodo=… — feature 016 · Dashboard.
    Abierta a cualquier usuario autenticado (las secciones de Ventas y
    Compras usan sus totales), pero la ganancia, su serie y su comparación
    solo se devuelven al admin (`016`, "Actualización: ganancias y
    movimientos de caja solo para admin").
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        rango = _rango_de(request)
        resumen = calcular_resumen(rango, usuario=_alcance(request))
        serializer = ResumenDashboardSerializer if _es_admin(request) else ResumenDashboardOperadorSerializer
        return Response(serializer(resumen).data)


class ResumenVentasView(APIView):
    """GET /api/reportes/ventas/?periodo= — desglose para la sección
    'Resumen de ventas' del Dashboard."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        resumen = calcular_resumen_ventas(_rango_de(request), usuario=_alcance(request))
        return Response(ResumenVentasSerializer(resumen).data)


class ResumenComprasView(APIView):
    """GET /api/reportes/compras/?periodo= — desglose para la sección
    'Resumen de compras' del Dashboard."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        resumen = calcular_resumen_compras(_rango_de(request), usuario=_alcance(request))
        return Response(ResumenComprasSerializer(resumen).data)


class ProductosTopView(APIView):
    """GET /api/reportes/productos-top/?periodo=&orden=mas|menos&por=cantidad|importe.
    El orden por importe es solo de admin (`016`, "Actualización: periodos
    ampliados, comparación y producción")."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        rango = _rango_de(request)
        orden = _validar_orden(request)
        por = request.query_params.get('por', TOP_PRODUCTOS_POR_CANTIDAD)
        if por not in TOP_PRODUCTOS_POR_VALIDOS:
            raise ValidationError({'por': f'Debe ser uno de: {", ".join(TOP_PRODUCTOS_POR_VALIDOS)}.'})
        if por == TOP_PRODUCTOS_POR_IMPORTE and not _es_admin(request):
            raise PermissionDenied('Solo el administrador puede ordenar los productos por importe.')

        resultados = calcular_top_productos(rango, orden, usuario=_alcance(request), por=por)
        serializer = ProductoTopImporteSerializer if por == TOP_PRODUCTOS_POR_IMPORTE else ProductoTopSerializer
        return Response(serializer(resultados, many=True).data)


class ClientesTopView(APIView):
    """GET /api/reportes/clientes-top/?periodo=&orden=mas|menos. El admin
    recibe el monto comprado; el operador, el número de compras, sin
    importes (`016`, "Actualización: ganancias y movimientos de caja solo
    para admin").
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        rango = _rango_de(request)
        orden = _validar_orden(request)
        if _es_admin(request):
            resultados = calcular_top_clientes(rango, orden, por=TOP_CLIENTES_POR_MONTO)
            return Response(ClienteTopSerializer(resultados, many=True).data)
        resultados = calcular_top_clientes(rango, orden, por=TOP_CLIENTES_POR_COMPRAS, usuario=request.user)
        return Response(ClienteTopOperadorSerializer(resultados, many=True).data)


class MovimientosCajaReporteView(APIView):
    """GET /api/reportes/movimientos-caja/?periodo=&limite=5|10|todos.

    Expone únicamente fecha/tipo/observación (nunca monto ni
    saldo_resultante), para la lista de "Movimientos financieros del
    periodo" del Dashboard. Solo admin desde `016`, "Actualización:
    ganancias y movimientos de caja solo para admin".
    """

    permission_classes = [EsAdmin]

    def get(self, request):
        rango = _rango_de(request)
        limite = request.query_params.get('limite', LIMITE_10)
        if limite not in LIMITES_VALIDOS:
            raise ValidationError({'limite': f'Debe ser uno de: {", ".join(LIMITES_VALIDOS)}.'})

        movimientos = obtener_movimientos_caja(rango, limite)
        return Response(MovimientoCajaReporteSerializer(movimientos, many=True).data)


class ResumenFacturacionView(APIView):
    """GET /api/reportes/facturacion/?periodo= — sección 'Resumen
    facturación' del Dashboard (`016`, "Actualización: Resumen facturación
    con datos"). Abierta a cualquier usuario autenticado, igual que
    Facturación, con el mismo contenido para ambos roles.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        resumen = calcular_resumen_facturacion(_rango_de(request), usuario=_alcance(request))
        return Response(ResumenFacturacionSerializer(resumen).data)


class ResumenProduccionView(APIView):
    """GET /api/reportes/produccion/?periodo= — sección 'Resumen de
    producción' del Dashboard (`016`, "Actualización: periodos ampliados,
    comparación y producción"). Toda la empresa para ambos roles, como el
    módulo Producción; el costo solo para el admin.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        admin = _es_admin(request)
        resumen = calcular_resumen_produccion(_rango_de(request), incluir_costo=admin)
        serializer = ResumenProduccionSerializer if admin else ResumenProduccionOperadorSerializer
        return Response(serializer(resumen).data)
