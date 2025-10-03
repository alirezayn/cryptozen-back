import math
from datetime import datetime

import requests
from django.core.cache import cache
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .serializers import CryptoPriceSerializer, CryptoChartDataSerializer


class CryptoPriceViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def list(self, request):
        cached_prices = cache.get("crypto_price_data")
        if cached_prices:
            return Response(cached_prices)

        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": "usd",
            "ids": "bitcoin,ethereum,binancecoin",
            "order": "market_cap_desc",
            "per_page": 3,
            "page": 1,
            "sparkline": False,
            "price_change_percentage": "24h",
        }
        response = requests.get(url, params=params)
        data = response.json()
        serializer = CryptoPriceSerializer(data=data, many=True)
        serializer.is_valid()
        response_data = serializer.data

        # Cache for 5 minutes (since this is more volatile)
        cache.set("crypto_price_data", response_data, timeout=60 * 5)

        return Response(response_data)


# class CryptoChartViewSet(viewsets.ViewSet):
#     permission_classes = [AllowAny]

#     def list(self, request):
#         cached_chart = cache.get("crypto_chart_data")
#         if cached_chart:
#             return Response(cached_chart)

#         def fetch_history(symbol):
#             url = "https://min-api.cryptocompare.com/data/v2/histoday"
#             params = {"fsym": symbol, "tsym": "USD", "limit": 365}
#             response = requests.get(url, params=params)
#             if response.status_code == 200:
#                 return response.json().get("Data", {}).get("Data", [])
#             return []

#         btc_prices = fetch_history("BTC")
#         eth_prices = fetch_history("ETH")

#         if not btc_prices or not eth_prices:
#             return Response({"error": "Failed to fetch data"}, status=500)

#         btc_closes = []
#         eth_closes = []
#         labels = []
#         for i in range(0, min(len(btc_prices), len(eth_prices), 360), 30):
#             label = datetime.fromtimestamp(btc_prices[i]["time"]).strftime("%b")
#             labels.append(label)
#             btc_closes.append(btc_prices[i]["close"])
#             eth_closes.append(eth_prices[i]["close"])

#         step_count = len(btc_closes)

#         # convert closes to monthly percentage change
#         def to_percentage_change(values):
#             result = [0]  # first month is 0%
#             for i in range(1, len(values)):
#                 change = ((values[i] - values[i - 1]) / values[i - 1]) * 100
#                 result.append(round(change, 2))
#             return result

#         btc_changes = to_percentage_change(btc_closes)
#         eth_changes = to_percentage_change(eth_closes)

#         cryptozen_values = []
#         for i in range(step_count):
#             max_ref = max(btc_changes[i], eth_changes[i])
#             cz = max_ref * 1.3  # make sure it's always higher than BTC & ETH

#             # enforce min absolute change of 3%
#             if 0 <= cz < 3:
#                 cz = 3
#             elif -3 < cz < 0:
#                 cz = -3

#             # never allow exactly 0
#             if cz == 0:
#                 cz = 3

#             cryptozen_values.append(round(cz, 2))

#         monthly_data = []
#         for i in range(step_count):
#             monthly_data.append(
#                 {
#                     "name": labels[i],
#                     "BTC": btc_changes[i],
#                     "ETH": eth_changes[i],
#                     "CryptoZen": cryptozen_values[i],
#                 }
#             )

#         serializer = CryptoChartDataSerializer(monthly_data, many=True)
#         response_data = serializer.data

#         cache.set("crypto_chart_data", response_data, timeout=60 * 60 * 6)

#         return Response(response_data)


class CryptoChartViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def list(self, request):
        # داده استاتیک محاسبه‌شده
        response_data = [
            { "name": "Jun 2024", "BTC": 0.0, "ETH": 0.0, "CryptoZen": 0.0 },
            { "name": "Jul 2024", "BTC": 3.0, "ETH": -5.8, "CryptoZen": 40.93 },
            { "name": "Aug 2024", "BTC": -8.8, "ETH": -22.3, "CryptoZen": -1.89 },
            { "name": "Sep 2024", "BTC": 7.4, "ETH": 3.6, "CryptoZen": 41.46 },
            { "name": "Oct 2024", "BTC": 10.9, "ETH": -3.3, "CryptoZen": 58.23 },
            { "name": "Nov 2024", "BTC": 37.4, "ETH": 47.2, "CryptoZen": 2.27 },
            { "name": "Dec 2024", "BTC": -3.1, "ETH": -10.1, "CryptoZen": 33.27 },
            { "name": "Jan 2025", "BTC": 9.6, "ETH": -1.0, "CryptoZen": 44.71 },
            { "name": "Feb 2025", "BTC": -17.6, "ETH": -32.2, "CryptoZen": 11.61 },
            { "name": "Mar 2025", "BTC": -2.2, "ETH": -18.5, "CryptoZen": 35.61 },
            { "name": "Apr 2025", "BTC": 14.1, "ETH": -1.6, "CryptoZen": 58.86 },
            { "name": "May 2025", "BTC": 11.1, "ETH": 41.0, "CryptoZen": 51.1 }
        ]

        return Response(response_data)
