from rest_framework.routers import SimpleRouter
from .views import GalleryImageViewSet, IntroductionContentViewSet

router = SimpleRouter()
router.register(r"gallery", GalleryImageViewSet, basename="gallery")
router.register(r"introduction", IntroductionContentViewSet, basename="introduction")

urlpatterns = router.urls
