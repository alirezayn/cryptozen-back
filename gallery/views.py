from rest_framework import viewsets, permissions
from .models import GalleryImage, IntroductionContent
from .serializers import GalleryImageSerializer, IntroductionContentSerializer


class GalleryImageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = GalleryImage.objects.all().order_by("-uploaded_at")
    serializer_class = GalleryImageSerializer
    permission_classes = [permissions.AllowAny]


class IntroductionContentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = IntroductionContent.objects.all()
    serializer_class = IntroductionContentSerializer
    permission_classes = [permissions.AllowAny]
