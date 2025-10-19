from rest_framework.routers import SimpleRouter
from .views import UserViewSet,confirm_verification_token
from django.urls import path 

router = SimpleRouter()
router.register(r"users", UserViewSet, basename="users")

urlpatterns = router.urls



urlpatterns += [
    path("users/verify/confirm_token/", confirm_verification_token, name="confirm_verification_token"),
]