from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from users.urls import router as users_router
from payments.urls import router as payments_router
from notifications.urls import router as notifications_router
from crypto.urls import router as crypto_router
from contact.urls import router as contact_router
from newsletter.urls import router as newsletter_router
from questions.urls import router as questions_router
from gallery.urls import router as gallery_router
from payments.views import NowPaymentsWebhook


urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/payment/webhook/", NowPaymentsWebhook.as_view(), name="cryptomus-webhook"),



    path("api/", include(users_router.urls)),
    path("api/", include(payments_router.urls)),
    path("api/", include(notifications_router.urls)),
    path("api/", include(crypto_router.urls)),
    path("api/", include(contact_router.urls)),
    path("api/", include(newsletter_router.urls)),
    path("api/", include(questions_router.urls)),
    path("api/", include(gallery_router.urls)),
    path("api/", include("wallet.urls")),

    # this app create by Devmix
    path("collab/", include("collab.urls")),
]

from users.views import CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns += [
    path("api/token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
