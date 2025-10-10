from rest_framework import serializers
from .models import UserWallet, WithdrawRequests
from decimal import Decimal

class UserWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserWallet
        fields = ["balance", "created_at"]
        read_only_fields = ["balance", "created_at"]


class WalletTransactionSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=20, decimal_places=8)

    def to_internal_value(self, data):
        # اول تبدیل به dict استاندارد
        ret = super().to_internal_value(data)

        # اگر amount به صورت int اومده باشه، به Decimal تبدیل می‌کنیم
        amount = ret.get("amount")
        if isinstance(amount, int):
            ret["amount"] = Decimal(amount)

        return ret

class WithdrawHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = WithdrawRequests
        fields = "__all__"