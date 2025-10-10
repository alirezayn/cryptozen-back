from rest_framework import serializers
from .models import GalleryImage, IntroductionContent


class GalleryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GalleryImage
        fields = ["id", "image", "caption"]


class IntroductionContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntroductionContent
        fields = ['id', 'title', 'video', 'poster_desktop', 'poster_mobile', 'description']