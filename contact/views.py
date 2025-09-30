from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import ContactMessage, UserComment
from .serializers import ContactMessageSerializer, UserCommentSerializer
from rest_framework.permissions import AllowAny


class ContactMessageViewSet(viewsets.ModelViewSet):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Your message has been sent!"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserCommentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UserComment.objects.all().order_by("-created_at")
    serializer_class = UserCommentSerializer
    permission_classes = [AllowAny]

    def get_serializer_context(self):
        return {"request": self.request}
