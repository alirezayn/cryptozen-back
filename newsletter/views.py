from .models import NewsletterSubscription
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .serializers import NewsletterSubscriptionSerializer
from rest_framework.response import Response
from rest_framework.permissions import AllowAny


class NewsletterSubscriptionViewSet(viewsets.ModelViewSet):
    queryset = NewsletterSubscription.objects.all()
    serializer_class = NewsletterSubscriptionSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required"}, status=400)

        # prevent duplicates
        if NewsletterSubscription.objects.filter(email=email).exists():
            return Response({"message": "Already subscribed"}, status=200)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Successfully subscribed!"}, status=201)

        return Response(serializer.errors, status=400)
