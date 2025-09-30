from django.core.exceptions import ValidationError
from django.db import transaction
from .models import UserWallet, WithdrawRequests
from payments.models import Payment
from payments.nowpayments_client import NowPaymentsClient
from django.conf import settings
from django.utils.timezone import now

class WalletService:
    @staticmethod
    def get_or_create_wallet(user):
        wallet, _ = UserWallet.objects.get_or_create(user=user)
        return wallet

    @staticmethod
    @transaction.atomic
    def deposit(user, amount):
        if amount <= 0:
            return {"success":False, "message": "Deposit amount must be greater than zero.", "data": None}
        callback_url = f"{settings.BACKEND_URL}/api/payment/webhook/"
        success_url = f"{settings.FRONTEND_URL}/payment/callback"
        cancel_url = f"{settings.FRONTEND_URL}/payment/cancel"
        order_id = f"{user.id}-{int(now().timestamp())}"
    
        res = NowPaymentsClient.create_invoice(
            amount=float(amount),
            currency="usd",
            order_id=order_id,
            description=f"Increasing your balance by {amount}",
            callback_url=callback_url,
            success_url=success_url,
            cancel_url=cancel_url,
        )
        if "invoice_url" not in res or "id" not in res:
            return {"success":False, "message": "Invoice creation failed", "data": res}
        
        Payment.objects.create(user=user, amount=amount, currency="USD", method="deposit", status="pending", cryptomus_payment_uuid=res["id"], payment_url=res["invoice_url"])
        WalletService.get_or_create_wallet(user)
        return {"success":True, "message": "Invoice created successfully", "data": res}

    @staticmethod
    @transaction.atomic
    def withdraw(user, amount):
        
        if amount <= 0:
            return {"success":False, "message": "Withdraw amount must be greater than zero.", "data": None}

        if WalletService.withdraw_request_exists(user):
            return {"success": False, "message": "You already have a pending withdraw request. please wait for it to be processed", "data": None}



        wallet = WalletService.get_or_create_wallet(user)
        
        if wallet.balance < amount:
            return {"success":False, "message": "Insufficient balance.", "data": None}
        
        return {"success":True, "message": "Withdraw request submitted successfully", "data": None}

    @staticmethod
    def get_balance(user):
        wallet = WalletService.get_or_create_wallet(user)
        return wallet.balance


    @staticmethod
    def withdraw_request_exists(user):
        return WithdrawRequests.objects.filter(user=user,status="pending").exists()
    
    @staticmethod
    def get_withdraw_requests(user):
        """Return all withdraw requests for a user as a QuerySet"""
        return WithdrawRequests.objects.filter(user=user).all()