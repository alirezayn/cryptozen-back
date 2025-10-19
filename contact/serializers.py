from rest_framework import serializers
from .models import ContactMessage, UserComment


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "message_type","message", "created_at"]


class UserCommentSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = UserComment
        fields = ["id", "name", "role", "image", "rating", "text", "created_at"]

    def get_image(self, obj):
        request = self.context.get("request")
        if obj.image and hasattr(obj.image, "url"):
            return request.build_absolute_uri(obj.image.url)
        return None
