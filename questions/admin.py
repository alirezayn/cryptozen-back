from django.contrib import admin
from .models import Question


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("number", "text", "type", "created_at")
    list_filter = ("type",)
    search_fields = ("text", "answer")
