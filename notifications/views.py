from rest_framework import viewsets, permissions
from .models import Notification
from .serializers import NotificationSerializer
from django.db.models import Q


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(
            Q(user=self.request.user) | Q(is_global=True),
            show=True,
        ).order_by("-created_at")
