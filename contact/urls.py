from rest_framework.routers import SimpleRouter
from .views import ContactMessageViewSet, UserCommentViewSet

router = SimpleRouter()
router.register(r"messages", ContactMessageViewSet, basename="messages")
router.register(r"comments", UserCommentViewSet, basename="comments")

urlpatterns = router.urls
