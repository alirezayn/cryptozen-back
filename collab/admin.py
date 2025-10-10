from django.contrib import admin
from .models import CollabLink

@admin.register(CollabLink)
class ReferralLinkAdmin(admin.ModelAdmin):
    list_display = ("owner", "url", "created_at","get_join_users","reward","cost_from_join_users")

    def get_join_users(self, obj):
        return ", ".join([str(u) for u in obj.join_users.all()])
    
    get_join_users.short_description = "Join Users"