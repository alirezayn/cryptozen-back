from django.urls import path
from .views import WalletBalanceView, WalletDepositView, WalletWithdrawView,WithdrawHistoryView

urlpatterns = [
    path("wallet/", WalletBalanceView.as_view(), name="wallet-balance"),
    path("wallet/deposit/", WalletDepositView.as_view(), name="wallet-deposit"),
    path("wallet/withdraw-request/", WalletWithdrawView.as_view(), name="wallet-withdraw-request"),
    path("wallet/withdraw-history/", WithdrawHistoryView.as_view(), name="wallet-withdraw-history"),
]