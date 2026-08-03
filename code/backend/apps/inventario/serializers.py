from rest_framework import serializers


class AlertaStockSerializer(serializers.Serializer):
    tipo = serializers.ChoiceField(choices=['producto', 'materia_prima'])
    nombre = serializers.CharField()
    sucursal = serializers.CharField()
    stock_actual = serializers.DecimalField(max_digits=12, decimal_places=2)
    stock_minimo = serializers.DecimalField(max_digits=12, decimal_places=2)
