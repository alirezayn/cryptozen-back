from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):
    model = User
    # Fields to display in the admin list view
    list_display = (
        "username",
        "email",
        "user_id",
        "telegram_id",
        "is_verified",
        "awaiting_verification",
        "referrals",
        "crypto_experience",
        "crypto_goal",
        "monthly_budget",
        "vip_interest",
        "is_active",
        "is_staff"
    )

    # Fields to filter by in the admin list view
    list_filter = (
        "is_verified",
        "awaiting_verification",
        "is_active",
        "is_staff",
        "crypto_experience",
        "crypto_goal",
        "monthly_budget",
        "vip_interest",
    )

    # Fields to search in the admin list view
    search_fields = (
        "username",
        "email",
        "user_id",
        "telegram_id",
        "email_verification_token",
    )

    # Organize fields in the detail view
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "username",
                    "password",
                ),
            },
        ),
        (
            "Personal Info",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "telegram_id",
                    "profile_image",
                ),
            },
        ),
        (
            "Referral Info",
            {
                "fields": (
                    "user_id",
                    "referral_link",
                    "referred_by",
                    "referrals",
                ),
            },
        ),
        (
            "Verification Info",
            {
                "fields": (
                    "is_verified",
                    "awaiting_verification",
                    "email_verification_token",
                ),
            },
        ),
        (
            "Profile Preferences",
            {
                "fields": (
                    "crypto_experience",
                    "crypto_goal",
                    "interests",
                    "trading_platforms",
                    "monthly_budget",
                    "vip_interest",
                    "learning_preference",
                    "crypto_years_active",
                ),
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (
            "Important dates",
            {
                "fields": (
                    "last_login",
                    "date_joined",
                ),
            },
        ),
    )

    # Fields to display when adding a new user
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "password1",
                    "password2",
                    "telegram_id",
                    "first_name",
                    "last_name",
                    "profile_image",
                ),
            },
        ),
    )

    # Read-only fields (to prevent accidental changes)
    readonly_fields = (
        "user_id",
        "referral_link",
        "referrals",
        "email_verification_token",
        "last_login",
        "date_joined",
    )

    # Order of fields in the list view
    ordering = ("username",)


admin.site.register(User, CustomUserAdmin)
