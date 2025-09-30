from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import Question
from .serializers import QuestionSerializer


class QuestionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = QuestionSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        question_type = self.request.query_params.get("type", "normal")
        return Question.objects.filter(type=question_type).order_by("number")

    def get_serializer_context(self):
        return {"request": self.request}
