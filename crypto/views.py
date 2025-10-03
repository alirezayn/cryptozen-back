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
            { "name": "Jun 2024", "BTC": 1000.0, "ETH": 1000.0, "CryptoZen": 1000.0 },
            { "name": "Jul 2024", "BTC": 1030.0, "ETH": 942.0, "CryptoZen": 1409.3 },
            { "name": "Aug 2024", "BTC": 939.36, "ETH": 731.93, "CryptoZen": 1382.66 },
            { "name": "Sep 2024", "BTC": 1008.87, "ETH": 758.28, "CryptoZen": 1955.91 },
            { "name": "Oct 2024", "BTC": 1118.84, "ETH": 733.26, "CryptoZen": 3094.84 },
            { "name": "Nov 2024", "BTC": 1537.29, "ETH": 1079.36, "CryptoZen": 3165.09 },
            { "name": "Dec 2024", "BTC": 1489.63, "ETH": 970.34, "CryptoZen": 4218.12 },
            { "name": "Jan 2025", "BTC": 1632.63, "ETH": 960.64, "CryptoZen": 6104.04 },
            { "name": "Feb 2025", "BTC": 1345.29, "ETH": 651.31, "CryptoZen": 6812.72 },
            { "name": "Mar 2025", "BTC": 1315.69, "ETH": 530.82, "CryptoZen": 9238.73 },
            { "name": "Apr 2025", "BTC": 1501.2, "ETH": 522.33, "CryptoZen": 14676.65 },
            { "name": "May 2025", "BTC": 1667.83, "ETH": 736.49, "CryptoZen": 22176.42 }
        ]

        return Response(response_data)
