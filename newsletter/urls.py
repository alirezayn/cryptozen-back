from rest_framework.routers import SimpleRouter
from .views import NewsletterSubscriptionViewSet

router = SimpleRouter()
router.register(r"newsletter", NewsletterSubscriptionViewSet, basename="newsletter")

urlpatterns = router.urls
