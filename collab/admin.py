from django.contrib import admin
from .models import CollabLink

@admin.register(CollabLink)
class ReferralLinkAdmin(admin.ModelAdmin):
    list_display = ("owner", "url", "created_at")