from django.urls import path
from .views import create_or_get_referral, register_link, receive_collab

urlpatterns = [
    path("generate/", create_or_get_referral, name="generate-collab"),
    path('invite/<str:referral_id>/', register_link, name='register-link'),
    path("receive-collab/", receive_collab, name="receive-collab"),
]