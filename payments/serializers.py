from rest_framework import serializers
from .models import (
    Subscription,
    PaymentHistory,
    SubscriptionPlan,
    DiscountedPlan,
    Payment,
)


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ["plan", "start_date", "end_date", "active"]


class PaymentHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentHistory
        fields = ["status", "method", "amount", "date"]


class PaymentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()  # or use user.username directly

    class Meta:
        model = Payment
        fields = ["user", "status", "method", "amount", "currency", "created_at","payment_id","cryptomus_payment_uuid"]


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    features = serializers.SerializerMethodField()

    class Meta:
        model = SubscriptionPlan
        fields = [
            "plan_type",
            "title",
            "description",
            "price",
            "price_note",
            "duration",
            "features",
        ]

    def get_features(self, obj):
        return obj.feature_list()


class DiscountedPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountedPlan
        fields = "__all__"
