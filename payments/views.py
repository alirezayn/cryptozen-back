from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from collab.models import CollabLink
from .models import (
    Subscription,
    PaymentHistory,
    SubscriptionPlan,
    DiscountedPlan,
    Payment,
)
from decimal import Decimal
from .serializers import (
    SubscriptionSerializer,
    PaymentHistorySerializer,
    PaymentSerializer,
    SubscriptionPlanSerializer,
    DiscountedPlanSerializer,
)
from .utils import send_payment_confirmation_email
from datetime import timedelta
from rest_framework.permissions import AllowAny,IsAuthenticated
from .nowpayments_client import NowPaymentsClient
from django.utils.timezone import now
from django.conf import settings
from rest_framework.views import APIView
from wallet.service import WalletService  
from django.core.exceptions import ValidationError
from rest_framework.request import Request 
from wallet.models import UserWallet
from dateutil.relativedelta import relativedelta

from decimal import Decimal





class SubscriptionViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    @action(detail=False, methods=["get"])
    def current(self, request:Request):
        try:
            sub = Subscription.objects.get(user=request.user, active=True)
            check = Payment.objects.filter(user=request.user).last()
            if check.status == "pending":
                sub.plan = check.pre_subscription
                sub.save()
            serializer = SubscriptionSerializer(sub)
            return Response(serializer.data)
        except Subscription.DoesNotExist:
            return Response({"status": "No subscription"})

    @action(detail=False, methods=["post"])
    def subscribe(self, request:Request):
        plan = request.data.get("plan")
        subscription_exists = Subscription.objects.filter(user=request.user,active=True,plan=plan).exists()
        # check = Payment.objects.filter(user=request.user,subscription=)
        pending_sub = Payment.objects.filter(user=request.user,status="pending").first()
        if pending_sub is not None:
            pending_sub.delete()
        if subscription_exists:
            return Response({
                "success":False,
                "message":"You have already subscribed this plan",
                "data":None
            },status=400)
        try:
            plan_data = SubscriptionPlan.objects.get(plan_type=plan)
            print(plan_data.months)
        except:
            return Response({"error": "Invalid plan"}, status=400)

        user = request.user
        price = plan_data.price

        wallet = WalletService.get_or_create_wallet(user)
        if wallet.balance >= price:
            try:
                WalletService.withdraw(user, price)
            except ValidationError as e:
                return Response({"error": str(e)}, status=400)

            subscription, _ = Subscription.objects.update_or_create(
                user=user,
                defaults={
                    "plan": plan,
                    "start_date": now().date(),
                    "end_date": now().date() + relativedelta(months=plan_data.months),
                    "active": True,
                },
            )

            Payment.objects.create(
                user=user,
                subscription=subscription,
                amount=price * plan_data.months,
                currency="USD",
                status="paid",
                method="withdraw",
                cryptomus_payment_uuid=f"internal-{now().timestamp()}",  # داخلی
            )

            # payed for collab
            link = CollabLink.objects.filter(join_users=user).first()
            if link:
                percent = Decimal(link.cost_from_join_users) / Decimal("100")
                link.reward += percent * float(price)
                link.save()

            return Response({"status": "Subscription activated using wallet balance.","payment_url": f"{settings.FRONTEND_URL}/dashboard"})

        order_id = f"{user.id}-{int(now().timestamp())}"

        callback_url = f"{settings.BACKEND_URL}/api/somepath/webhook/some/"
        success_url = f"{settings.FRONTEND_URL}/payment/callback"
        cancel_url = f"{settings.FRONTEND_URL}/payment/cancel"

        res = NowPaymentsClient.create_invoice(
            amount=float(price) * plan_data.months,
            currency="usd",
            order_id=order_id,
            description=f"CryptoZen VIP Subscription - {plan.capitalize()} Plan",
            callback_url=callback_url,
            success_url=success_url,
            cancel_url=cancel_url,
        )

        if "invoice_url" not in res or "id" not in res:
            return Response(
                {"error": "Invoice creation failed", "details": res}, status=400
            )

        subscription, _ = Subscription.objects.update_or_create(
            user=user,
            defaults={
                "plan": plan,
                "end_date": now().date() + relativedelta(months=plan_data.months),
                "active": False,
            },
        )

        Payment.objects.create(
            user=user,
            subscription=subscription,
            amount=price * plan_data.months,
            currency="USD",
            status="pending",
            payment_url=res["invoice_url"],
            cryptomus_payment_uuid=res["id"]
        )

        # payed for collab
        link = CollabLink.objects.filter(join_users=user).first()
        if link:
            percent = Decimal(link.cost_from_join_users) / Decimal("100")

            
            link.reward += percent * price
            link.save()

        return Response({"payment_url": res["invoice_url"]})


    @action(methods=["post"], detail=False)
    def upgrade_plan(self, request: Request):
        user = request.user
        plan = request.data.get("plan")

        # بررسی تکراری بودن اشتراک فعال
        subscription_exists = Subscription.objects.filter(
            user=user, active=True, plan=plan
        ).exists()
        if subscription_exists:
            return Response({
                "success": False,
                "message": "You have already subscribed to this plan",
                "data": None
            }, status=400)

        try:
            subscription_plan = SubscriptionPlan.objects.get(plan_type=plan)
        except SubscriptionPlan.DoesNotExist:
            return Response({"success": False, "message": "Invalid plan"}, status=400)

        # حذف پرداخت‌های pending قبلی
        pending_sub = Payment.objects.filter(user=user, status="pending").first()
        if pending_sub:
            pending_sub.delete()

        # اشتراک فعلی کاربر
        user_current_subscription = Subscription.objects.filter(user=user).first()

        order_id = f"{user.id}-{int(now().timestamp())}"
        callback_url = f"{settings.BACKEND_URL}/api/nowpayments/webhook/"
        success_url = f"{settings.FRONTEND_URL}/payment/callback"
        cancel_url = f"{settings.FRONTEND_URL}/payment/cancel"

        # ساخت رکورد پرداخت جدید
        upgrade_payment = Payment.objects.create(
            user=user,
            subscription=user_current_subscription,
            pre_subscription=user_current_subscription.plan if user_current_subscription else None,
            next_subscription=plan,  # ← پلن جدید اینجا ذخیره میشه
            amount=subscription_plan.price * subscription_plan.months,
            currency="USD",
            method="crypto",
            status="pending",
        )

        try:
            res = NowPaymentsClient.create_invoice(
                amount=float(subscription_plan.price) * subscription_plan.months,
                currency="usd",
                order_id=order_id,
                description=f"CryptoZen VIP Subscription - {plan.capitalize()} Plan",
                callback_url=callback_url,
                success_url=success_url,
                cancel_url=cancel_url,
            )
            if "invoice_url" not in res or "id" not in res:
                return Response({"error": "Invoice creation failed", "details": res}, status=400)
        except Exception as e:
            return Response({"success": False, "message": f"Invoice creation failed: {str(e)}"}, status=400)

        upgrade_payment.payment_url = res["invoice_url"]
        upgrade_payment.cryptomus_payment_uuid = res["id"]
        upgrade_payment.save()

        return Response({"payment_url": res["invoice_url"]})

# @method_decorator(csrf_exempt, name='dispatch')
class NowPaymentsWebhook(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        payment_id = data.get("id")

        if not payment_id:
            return Response({"success": False, "message": "Missing payment ID"}, status=400)

        # دریافت اطلاعات پرداخت از NowPayments API
        try:
            now_payment = NowPaymentsClient.get_invoice(payment_id)
        except Exception as e:
            return Response({"success": False, "message": f"Error fetching invoice: {str(e)}"}, status=400)

        try:
            payment = Payment.objects.get(cryptomus_payment_uuid=now_payment["invoice_id"])
        except Payment.DoesNotExist:
            return Response({"success": False, "message": "Payment not found"}, status=404)

        # ایجاد کیف پول کاربر در صورت عدم وجود
        wallet, _ = UserWallet.objects.get_or_create(user=payment.user)

        # ذخیره شناسه پرداخت
        payment.payment_id = now_payment.get("payment_id")
        payment.save()

        # جلوگیری از تکرار پردازش پرداخت موفق
        if payment.status in ["paid", "partial"] and payment.subscription and payment.subscription.active:
            return Response({
                "success": True,
                "message": "Payment already processed",
                "data": PaymentSerializer(payment).data
            }, status=200)

        # اگر نوع پرداخت Deposit باشد (افزایش موجودی کیف پول)
        if payment.method == "deposit":
            wallet.balance += Decimal(now_payment["price_amount"])
            wallet.save()
            payment.status = "paid"
            payment.save()

            send_payment_confirmation_email(
                user=payment.user,
                plan_type="Deposit",
                amount=now_payment["price_amount"],
                purpose="Deposit",
            )

            return Response({
                "success": True,
                "message": f"Wallet balance increased by {now_payment['price_amount']}",
                "data": PaymentSerializer(payment).data
            }, status=200)

        # بررسی وضعیت پرداخت در NowPayments
        payment_status = now_payment.get("payment_status")
        paid_amount = Decimal(str(now_payment.get("price_amount", "0")))

        try:
            subscription = payment.subscription
            plan = SubscriptionPlan.objects.get(plan_type=subscription.plan)
        except Exception:
            return Response({"success": False, "message": "Invalid subscription or plan"}, status=404)

        plan_price = plan.price

        # --- وضعیت پرداخت موفق ---
        if payment_status == "finished":
            # پرداخت ناقص (partial payment)
            if paid_amount < plan_price and payment.status not in ["partial", "paid"]:
                payment.status = "partial"
                payment.amount = paid_amount
                wallet.balance += paid_amount
                wallet.save()
                payment.save()

                return Response({
                    "success": True,
                    "message": f"Partial payment received. You need {plan_price - paid_amount} USD more to activate subscription.",
                    "data": PaymentSerializer(payment).data
                }, status=200)

            # پرداخت کامل (full payment)
            elif paid_amount >= plan_price:
                wallet.balance += paid_amount
                wallet.save()

                subscription.active = True

                # ✅ اگر کاربر قصد ارتقا داشته (پلن مقصد در payment.next_subscription ذخیره شده)
                if payment.next_subscription:
                    new_plan_type = payment.next_subscription
                    try:
                        new_plan = SubscriptionPlan.objects.get(plan_type=new_plan_type)
                    except SubscriptionPlan.DoesNotExist:
                        return Response({"success": False, "message": "Invalid target plan"}, status=400)

                    remaining_days = max((subscription.end_date - now().date()).days, 0)
                    subscription.plan = new_plan_type
                    subscription.start_date = now().date()
                    subscription.end_date = now().date() + relativedelta(
                        months=new_plan.months
                    ) + timedelta(days=remaining_days)
                    subscription.want_to_upgrade = False
                else:
                    # اگر ارتقا در کار نیست (تمدید یا اشتراک جدید)
                    subscription.start_date = now().date()
                    subscription.end_date = now().date() + relativedelta(months=plan.months)

                subscription.save()

                # ثبت پرداخت
                payment.status = "paid"
                payment.save()

                # از حساب کیف پول کم کن (در صورت استفاده از balance داخلی)
                wallet.balance -= paid_amount
                wallet.save()

                # ارسال ایمیل تأیید پرداخت
                send_payment_confirmation_email(
                    user=payment.user,
                    plan_type=payment.next_subscription or plan.plan_type,
                    amount=paid_amount,
                    purpose="Subscription",
                    subscription_end_date=subscription.end_date,
                )

                return Response({
                    "success": True,
                    "message": "Subscription activated successfully",
                    "data": PaymentSerializer(payment).data
                }, status=200)

        # --- وضعیت پرداخت ناموفق ---
        elif payment_status in ["expired", "failed"]:
            payment.status = "failed"
            payment.save()

            if payment.subscription:
                payment.subscription.active = False
                payment.subscription.save()

            return Response({
                "success": False,
                "message": "Subscription activation failed. Payment status is failed or expired.",
                "data": PaymentSerializer(payment).data
            }, status=400)

        # --- سایر وضعیت‌ها ---
        return Response({
            "success": False,
            "message": "Invalid or unrecognized payment status",
            "data": PaymentSerializer(payment).data
        }, status=400)







class PaymentHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PaymentHistorySerializer

    def get_queryset(self):
        return PaymentHistory.objects.filter(user=self.request.user,status="success")


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PaymentSerializer

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user).exclude(status="pending")


class SubscriptionPlanViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [AllowAny]


class DiscountedPlanViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DiscountedPlan.objects.all().order_by("id")
    serializer_class = DiscountedPlanSerializer
    permission_classes = [AllowAny]



