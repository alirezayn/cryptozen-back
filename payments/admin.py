from django.contrib import admin
from .models import (
    Subscription,
    PaymentHistory,
    SubscriptionPlan,
    DiscountedPlan,
    Payment,
)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ["user", "plan", "start_date", "end_date", "active"]
    search_fields = ["user__username", "plan"]
    list_filter = ["plan", "active"]
    readonly_fields = ["start_date"]


@admin.register(PaymentHistory)
class PaymentHistoryAdmin(admin.ModelAdmin):
    list_display = ["user", "amount", "method", "status", "date"]
    list_filter = ["status", "method"]
    search_fields = ["user__username"]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["user", "amount", "currency", "method", "status", "created_at"]
    list_filter = ["status", "method", "currency"]
    search_fields = ["user__username", "cryptomus_payment_uuid"]
    readonly_fields = ["created_at"]


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ("title", "plan_type", "price", "duration","months")
    list_filter = ("plan_type",)
    search_fields = ("title", "description", "features")
    ordering = ("plan_type",)


@admin.register(DiscountedPlan)
class DiscountedPlanAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "duration",
        "original_price",
        "discounted_price",
        "highlight_text",
    )
