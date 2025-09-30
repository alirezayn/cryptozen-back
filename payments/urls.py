from rest_framework.routers import SimpleRouter
from django.urls import path
from .views import (
    SubscriptionViewSet,
    PaymentHistoryViewSet,
    PaymentViewSet,
    SubscriptionPlanViewSet,
    DiscountedPlanViewSet,
    NowPaymentsWebhook,  # ⬅️ import webhook view
)

router = SimpleRouter()
router.register(r"subscriptions", SubscriptionViewSet, basename="subscriptions")
router.register(r"payments", PaymentViewSet, basename="payments")
router.register(r"plans", SubscriptionPlanViewSet, basename="plans")
router.register(r"discount", DiscountedPlanViewSet, basename="discount")

urlpatterns = [
    # path(
    #     # "somepath/webhook/some/", NowPaymentsWebhook.as_view(), name="cryptomus-webhook"
    # ),  # ⬅️ webhook endpoint
]

urlpatterns += router.urls
