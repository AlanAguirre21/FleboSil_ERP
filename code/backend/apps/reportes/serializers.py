from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from core.permissions import es_admin

from .services import (
    GRANULARIDAD_DIA,
    GRANULARIDAD_HORA,
    GRANULARIDAD_MES,
    GRANULARIDAD_SEMANA,
    MAXIMO_DIAS_PERSONALIZADO,
    PERIODO_DIA,
    PERIODO_PERSONALIZADO,
    PERIODOS_VALIDOS,
)

GRANULARIDADES = [GRANULARIDAD_HORA, GRANULARIDAD_DIA, GRANULARIDAD_SEMANA, GRANULARIDAD_MES]
MENSAJE_SOLO_DIA = 'Tu rol solo puede consultar el periodo Día.'


class ParametrosPeriodoSerializer(serializers.Serializer):
    """Parámetros de periodo de todos los endpoints de `reportes` (`016`,
    "Actualización: periodos ampliados, comparación y producción").

    Única capa de validación del periodo, incluida la restricción de rol: un
    usuario no admin solo consulta `dia` (403 con cualquier otro periodo o
    con `desde`/`hasta`). Requiere `request` en el contexto.
    """

    periodo = serializers.ChoiceField(
        choices=PERIODOS_VALIDOS,
        default=PERIODO_DIA,
        error_messages={'invalid_choice': f'Debe ser uno de: {", ".join(PERIODOS_VALIDOS)}.'},
    )
    desde = serializers.DateField(
        required=False, error_messages={'invalid': 'Fecha "Desde" inválida; usa el formato AAAA-MM-DD.'},
    )
    hasta = serializers.DateField(
        required=False, error_messages={'invalid': 'Fecha "Hasta" inválida; usa el formato AAAA-MM-DD.'},
    )

    def validate(self, attrs):
        usuario = self.context['request'].user
        periodo = attrs['periodo']
        trae_fechas = 'desde' in self.initial_data or 'hasta' in self.initial_data

        if not es_admin(usuario) and (periodo != PERIODO_DIA or trae_fechas):
            raise PermissionDenied(MENSAJE_SOLO_DIA)

        if periodo != PERIODO_PERSONALIZADO:
            # Las fechas solo aplican al periodo personalizado.
            attrs.pop('desde', None)
            attrs.pop('hasta', None)
            return attrs

        desde, hasta = attrs.get('desde'), attrs.get('hasta')
        errores = {}
        if desde is None:
            errores['desde'] = 'Indica la fecha "Desde".'
        if hasta is None:
            errores['hasta'] = 'Indica la fecha "Hasta".'
        if errores:
            raise serializers.ValidationError(errores)
        if desde > hasta:
            raise serializers.ValidationError({'desde': '"Desde" no puede ser posterior a "Hasta".'})
        if hasta > timezone.localdate():
            raise serializers.ValidationError({'hasta': '"Hasta" no puede ser posterior a hoy.'})
        if (hasta - desde).days + 1 > MAXIMO_DIAS_PERSONALIZADO:
            raise serializers.ValidationError({'hasta': 'El rango no puede ser mayor a 2 años (731 días).'})
        return attrs


def _porcentaje():
    return serializers.DecimalField(max_digits=8, decimal_places=1, allow_null=True)


def _monto(**kwargs):
    return serializers.DecimalField(max_digits=12, decimal_places=2, **kwargs)


class PeriodoAnteriorSerializer(serializers.Serializer):
    """Fechas (hora local) del periodo anterior contra el que se compara."""

    inicio = serializers.CharField()
    fin = serializers.CharField()


class ComparacionResumenSerializer(serializers.Serializer):
    ventas_total = _monto()
    compras_total = _monto()
    ganancia = _monto()


class VariacionResumenSerializer(serializers.Serializer):
    ventas_total = _porcentaje()
    compras_total = _porcentaje()
    ganancia = _porcentaje()


class ComparacionResumenOperadorSerializer(serializers.Serializer):
    ventas_total = _monto()
    compras_total = _monto()


class VariacionResumenOperadorSerializer(serializers.Serializer):
    ventas_total = _porcentaje()
    compras_total = _porcentaje()


class PuntoResumenSerializer(serializers.Serializer):
    fecha = serializers.CharField()
    ganancia = serializers.DecimalField(max_digits=12, decimal_places=2)


class ResumenDashboardSerializer(serializers.Serializer):
    periodo = serializers.ChoiceField(choices=PERIODOS_VALIDOS)
    granularidad = serializers.ChoiceField(choices=GRANULARIDADES)
    ventas_total = serializers.DecimalField(max_digits=12, decimal_places=2)
    compras_total = serializers.DecimalField(max_digits=12, decimal_places=2)
    ganancia = serializers.DecimalField(max_digits=12, decimal_places=2)
    serie = PuntoResumenSerializer(many=True)
    periodo_anterior = PeriodoAnteriorSerializer()
    anterior = ComparacionResumenSerializer()
    variacion = VariacionResumenSerializer()


class ResumenDashboardOperadorSerializer(serializers.Serializer):
    """Resumen para el operador: los totales que usan las secciones de Ventas
    y Compras, sin la ganancia, su serie ni su comparación (solo admin)."""

    periodo = serializers.ChoiceField(choices=PERIODOS_VALIDOS)
    ventas_total = serializers.DecimalField(max_digits=12, decimal_places=2)
    compras_total = serializers.DecimalField(max_digits=12, decimal_places=2)
    periodo_anterior = PeriodoAnteriorSerializer()
    anterior = ComparacionResumenOperadorSerializer()
    variacion = VariacionResumenOperadorSerializer()


class PuntoMontoSerializer(serializers.Serializer):
    fecha = serializers.CharField()
    monto = serializers.DecimalField(max_digits=12, decimal_places=2)


class ConteoEstadoSerializer(serializers.Serializer):
    tipo = serializers.CharField()
    cantidad = serializers.IntegerField()


class ComparacionVentasSerializer(serializers.Serializer):
    numero_ventas = serializers.IntegerField()
    ticket_promedio = _monto(allow_null=True)


class VariacionVentasSerializer(serializers.Serializer):
    numero_ventas = _porcentaje()
    ticket_promedio = _porcentaje()


class ResumenVentasSerializer(serializers.Serializer):
    periodo = serializers.ChoiceField(choices=PERIODOS_VALIDOS)
    granularidad = serializers.ChoiceField(choices=GRANULARIDADES)
    con_envio = PuntoMontoSerializer(many=True)
    sin_envio = PuntoMontoSerializer(many=True)
    envio = PuntoMontoSerializer(many=True)
    conteo_estado = ConteoEstadoSerializer(many=True)
    numero_ventas = serializers.IntegerField()
    ticket_promedio = _monto(allow_null=True)
    periodo_anterior = PeriodoAnteriorSerializer()
    anterior = ComparacionVentasSerializer()
    variacion = VariacionVentasSerializer()


class ResumenComprasSerializer(serializers.Serializer):
    periodo = serializers.ChoiceField(choices=PERIODOS_VALIDOS)
    granularidad = serializers.ChoiceField(choices=GRANULARIDADES)
    todas = PuntoMontoSerializer(many=True)
    productos = PuntoMontoSerializer(many=True)
    insumos = PuntoMontoSerializer(many=True)
    conteo_estado = ConteoEstadoSerializer(many=True)


class ProductoTopSerializer(serializers.Serializer):
    producto = serializers.CharField()
    cantidad = serializers.DecimalField(max_digits=12, decimal_places=2)


class ProductoTopImporteSerializer(serializers.Serializer):
    """Top de productos por importe vendido (solo admin)."""

    producto = serializers.CharField()
    importe = _monto()


class ClienteTopSerializer(serializers.Serializer):
    cliente = serializers.CharField()
    monto = serializers.DecimalField(max_digits=12, decimal_places=2)


class ClienteTopOperadorSerializer(serializers.Serializer):
    """Top de clientes para el operador: número de compras, sin importes
    (`016`, "Actualización: ganancias y movimientos de caja solo para admin")."""

    cliente = serializers.CharField()
    compras = serializers.IntegerField()


class MovimientoCajaReporteSerializer(serializers.Serializer):
    fecha = serializers.DateTimeField()
    tipo_movimiento = serializers.CharField()
    observacion = serializers.CharField()


# --- Resumen facturación (`016`, "Actualización: Resumen facturación con datos")


class PuntoFacturacionSerializer(serializers.Serializer):
    fecha = serializers.CharField()
    total = serializers.DecimalField(max_digits=12, decimal_places=2)
    pue = serializers.DecimalField(max_digits=12, decimal_places=2)
    ppd = serializers.DecimalField(max_digits=12, decimal_places=2)


class ConteoEstadoFacturaSerializer(serializers.Serializer):
    estado = serializers.CharField()
    tipo = serializers.CharField()
    cantidad = serializers.IntegerField()


class FacturaPorAtenderSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    serie = serializers.CharField(allow_blank=True)
    folio_interno = serializers.IntegerField(allow_null=True)
    cliente = serializers.CharField()
    total = serializers.DecimalField(max_digits=12, decimal_places=2)
    estado = serializers.CharField()
    fecha = serializers.DateTimeField()


class ComparacionFacturacionSerializer(serializers.Serializer):
    facturado_total = _monto()


class VariacionFacturacionSerializer(serializers.Serializer):
    facturado_total = _porcentaje()


class ResumenFacturacionSerializer(serializers.Serializer):
    periodo = serializers.ChoiceField(choices=PERIODOS_VALIDOS)
    granularidad = serializers.ChoiceField(choices=GRANULARIDADES)
    facturado_total = serializers.DecimalField(max_digits=12, decimal_places=2)
    facturas_emitidas = serializers.IntegerField()
    por_cobrar_ppd = serializers.DecimalField(max_digits=12, decimal_places=2)
    porcentaje_facturado = serializers.DecimalField(max_digits=5, decimal_places=1, allow_null=True)
    serie = PuntoFacturacionSerializer(many=True)
    conteo_estado = ConteoEstadoFacturaSerializer(many=True)
    requiere_atencion = FacturaPorAtenderSerializer(many=True)
    periodo_anterior = PeriodoAnteriorSerializer()
    anterior = ComparacionFacturacionSerializer()
    variacion = VariacionFacturacionSerializer()


# --- Resumen producción (`016`, "Actualización: periodos ampliados,
# comparación y producción")


class PuntoUnidadesSerializer(serializers.Serializer):
    fecha = serializers.CharField()
    unidades = _monto()


class ProductoProducidoSerializer(serializers.Serializer):
    producto = serializers.CharField()
    cantidad = _monto()


class ResumenProduccionOperadorSerializer(serializers.Serializer):
    """Resumen de producción sin el costo (información financiera)."""

    periodo = serializers.ChoiceField(choices=PERIODOS_VALIDOS)
    granularidad = serializers.ChoiceField(choices=GRANULARIDADES)
    producciones = serializers.IntegerField()
    unidades_producidas = _monto()
    serie = PuntoUnidadesSerializer(many=True)
    top_productos = ProductoProducidoSerializer(many=True)


class ResumenProduccionSerializer(ResumenProduccionOperadorSerializer):
    costo_total = _monto()
