from rest_framework.routers import SimpleRouter
from .views import QuestionViewSet

router = SimpleRouter()
router.register(r"questions", QuestionViewSet, basename="questions")

urlpatterns = router.urls
