# crypto/urls.py

from rest_framework.routers import SimpleRouter
from .views import CryptoChartViewSet, CryptoPriceViewSet

router = SimpleRouter()
router.register(r"crypto/prices", CryptoPriceViewSet, basename="crypto-prices")
router.register(r"crypto/chart", CryptoChartViewSet, basename="crypto-chart")

urlpatterns = router.urls
