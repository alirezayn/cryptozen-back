from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["title", "is_global", "user", "created_at"]
    list_filter = ["is_global"]
    search_fields = ["title", "message", "user__username"]
