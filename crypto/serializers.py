from rest_framework import serializers


class CryptoPriceSerializer(serializers.Serializer):
    id = serializers.CharField()
    symbol = serializers.CharField()
    name = serializers.CharField()
    image = serializers.URLField()
    current_price = serializers.FloatField()
    price_change_percentage_24h = serializers.FloatField()


class CryptoChartDataSerializer(serializers.Serializer):
    name = serializers.CharField()
    BTC = serializers.FloatField()
    ETH = serializers.FloatField()
    CryptoZen = serializers.FloatField()
