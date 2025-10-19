from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from collab.models import CollabLink
from .models import User
from .serializers import (
    UserSerializer,
    UserProfileSerializer,
    CustomTokenObtainPairSerializer,
    VerificationStatusSerializer,
    ProfileAnswersSerializer,
)
from django.utils.crypto import get_random_string
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from email.mime.image import MIMEImage
import os
from payments.models import Subscription, Payment
from datetime import timedelta
from django.utils.timezone import now
from django.contrib.auth import authenticate
# from django.contrib.auth.models import update_last_login
from rest_framework.request import Request
from django.db.models import Q
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UserViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["get"])
    def profile(self, request):
        user = request.user
        # 🔁 Cancel pending payments older than 30 min
        try:
            sub = Subscription.objects.get(user=user)
            if not sub.active:
                pending_payment = (
                    Payment.objects.filter(subscription=sub, status="pending")
                    .order_by("-created_at")
                    .first()
                )

                if pending_payment:
                    age_minutes = (
                                          now() - pending_payment.created_at
                                  ).total_seconds() / 60
                    if age_minutes > 30:
                        pending_payment.status = "cancelled"
                        pending_payment.save()
                        sub.active = False
                        sub.save()
        except Subscription.DoesNotExist:
            pass

        # 📤 Return user profile
        serializer = UserProfileSerializer(user, context={"request": request})
        return Response(serializer.data)

    @action(detail=False, methods=["post"], permission_classes=[permissions.AllowAny])
    def signup(self, request:Request):

        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            referral_id = request.data.get("referral_id")
            if referral_id:
                try:
                    collab_user = User.objects.get(user_id=referral_id)
                    link = CollabLink.objects.get(owner=collab_user)
                    link.join_users.add(user)
                    link.save()
                    collab_user.referrals += 1 
                    collab_user.save()

                except Exception as e:
                    print(e)
            else:
                CollabLink.objects.create(owner=user)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["put"], url_path="update-profile")
    def update_profile(self, request:Request):
        user = request.user
        data = request.data
        if "username" in data:
            if User.objects.exclude(id=user.id).filter(username=data["username"]).exists():
                return Response({"error": "This username is already taken."}, status=400)

        if "email" in data:
            if User.objects.exclude(id=user.id).filter(email=data["email"]).exists():
                return Response({"error": "This email is already in use."}, status=400)

        if "telegram_id" in data:
            if User.objects.exclude(id=user.id).filter(telegram_id=data["telegram_id"]).exists():
                return Response({"error": "This Telegram ID is already in use."}, status=400)





        # Update fields if they are provided in request
        if "username" in request.data:
            user.username = request.data["username"]
        if "first_name" in request.data:
            user.first_name = request.data["first_name"]
        if "last_name" in request.data:
            user.last_name = request.data["last_name"]
        if "telegram_id" in request.data:
            user.telegram_id = request.data["telegram_id"]
        if "email" in request.data:
            user.email = request.data["email"]

        # Password change section
        if "password" in request.data and "current_password" in request.data:
            if not user.check_password(request.data["current_password"]):
                return Response({"error": "Current password is incorrect"}, status=400)
            user.set_password(request.data["password"])

        # Profile image
        if "profile_image" in request.FILES:
            user.profile_image = request.FILES["profile_image"]

        user.save()

        serializer = UserProfileSerializer(user, context={"request": request})
        return Response({"message": "Profile updated", "data": serializer.data})
    @action(detail=False, methods=["post"], url_path="verify/start")
    def start_verification(self, request:Request):
        user = request.user
        email = request.data.get("email")
        telegram_id = request.data.get("telegram_id")

        if not email or not telegram_id:
            return Response({"error": "Email and Telegram ID required"}, status=400)

        user.email = email
        user.telegram_id = telegram_id
        user.is_verified = False
        user.awaiting_verification = True
        user.generate_verification_token()

        verification_link = f"{settings.FRONTEND_URL}/dashboard/?verify_token={user.email_verification_token}"
        html_content = render_to_string(
            "email/verify_email.html",
            {"verification_link": verification_link, "user_id": user.user_id, "fullname": user.first_name + " " + user.last_name,"verification_code": user.user_id},
        )

        email_msg = EmailMultiAlternatives(
            subject="Verify your CryptoZen Account",
            body="Click the button to confirm your email.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email_msg.attach_alternative(html_content, "text/html")

        # Embed logo
        # logo_path = os.path.join(settings.BASE_DIR, "users/templates/email/logo.png")
        # with open(logo_path, "rb") as f:
        #     logo = MIMEImage(f.read())
        #     logo.add_header("Content-ID", "<logo_image>")
        #     logo.add_header("Content-Disposition", "inline", filename="logo.png")
        #     email_msg.attach(logo)

        email_msg.send()

        return Response({"message": "Verification email sent"})

    # @action(
    #     detail=False,
    #     methods=["get"],
    #     url_path="verify/confirm_token",
    #     permission_classes=[AllowAny],
    # )
    # def confirm_verification(self, request:Request, token=None):
    #     token = request.query_params.get("token")
    #     if not token:
    #         return Response({"error": "Token not provided"}, status=400)


    #     try:
    #         user = User.objects.get(email_verification_token=token)
    #         user.is_verified = True
    #         user.awaiting_verification = False
    #         user.email_verification_token = None
    #         user.save()

    #         # Send confirmation VIP welcome email
    #         html_content = render_to_string(
    #             "email/confirm_verify.html",
    #             {
    #                 "user_id": user.user_id,
    #                 "user_name": user.username,
    #                 "activation_code": user.user_id,  # you can generate real code here
    #                 "admin_username": "@cryptozen360",  # change this
    #                 "website_url": "https://cryptozen360.com",
    #                 "twitter_url": "https://x.com/cryptozen360",
    #                 "support_email": "cryptozen360@gmail.com",
    #             },
    #         )

    #         email_msg = EmailMultiAlternatives(
    #             subject="🎉 Welcome to CryptoZen VIP – You're In!",
    #             body="You're now a VIP! Check your Telegram for access.",
    #             from_email=settings.DEFAULT_FROM_EMAIL,
    #             to=[user.email],
    #         )
    #         email_msg.attach_alternative(html_content, "text/html")

    #         # Embed logo
    #         logo_path = os.path.join(
    #             settings.BASE_DIR, "users/templates/email/logo.png"
    #         )
    #         with open(logo_path, "rb") as f:
    #             logo = MIMEImage(f.read())
    #             logo.add_header("Content-ID", "<logo_image>")
    #             logo.add_header("Content-Disposition", "inline", filename="logo.png")
    #             email_msg.attach(logo)

    #         email_msg.send()

    #         return Response({"message": "Email verified successfully"})

    #     except User.DoesNotExist:
    #         return Response(
    #             {"error": "Invalid or expired verification token"},
    #             status=status.HTTP_400_BAD_REQUEST,
    #         )

    @action(detail=False, methods=["get"], url_path="verify/status")
    def verification_status(self, request):
        return Response(
            {
                "is_verified": request.user.is_verified,
                "awaiting_verification": request.user.awaiting_verification,
            }
        )

    @action(detail=False, methods=["post"], url_path="profile/answers")
    def save_profile_answers(self, request):
        serializer = ProfileAnswersSerializer(
            request.user, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile answers saved successfully"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # code by Devmix
    @action(detail=False, methods=["post"], url_path="verify/confirm", permission_classes=[permissions.AllowAny],
            authentication_classes=[])
    def confirm_verification(self, request:Request):
        """this function is check code as send by user , find user by its email."""

        email = request.data.get("email")
        code = request.data.get("code")

        if not email or not code:
            return Response({"error": "Email and code are required."}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=404)

        if str(user.user_id) != str(code).upper():
            return Response({"error": "Invalid verification code."}, status=400)

        user.is_verified = True
        user.awaiting_verification = True
        user.save()

        return Response({"message": "Email verified successfully."}, status=200)

    @action(detail=False, methods=["post"], url_path="check/info", permission_classes=[permissions.AllowAny],
            authentication_classes=[])
    def check_information(self, request:Request):
        """Check username & password validity"""
        username = request.data.get("username")
        password = request.data.get("password")


        find_user = User.objects.filter(Q(username=username) | Q(email=username)).first()


        if find_user is None:
            return Response(
                {"error": "Invalid username or password."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not username or not password:
            return Response(
                {"error": "Username and password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=find_user.username, password=password)
        if user is not None:
            return Response(
                {"success": True, "message": "Password is correct."},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"success": False, "message": "Invalid username or password."},
                status=status.HTTP_401_UNAUTHORIZED
            )

    @action(detail=False, methods=["post"], permission_classes=[permissions.AllowAny], authentication_classes=[])
    def login(self, request:Request):
        """Authenticate user and return JWT tokens"""
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"error": "Username and password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        find_user = User.objects.filter(Q(username=username) | Q(email=username)).first()
        
        if find_user is None:
            return Response(
                {"error": "Invalid username or password."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        user = authenticate(username=find_user.username, password=password)

        if user is None:
            return Response(
                {"error": "Invalid username or password."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        CollabLink.objects.get_or_create(owner=user)


        user_data = UserProfileSerializer(user, context={"request": request}).data

        return Response({
            "token": access_token,
            "refresh_token": refresh_token,
            "user": user_data,
            "message": "Login successful."
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=["post"], permission_classes=[permissions.AllowAny], authentication_classes=[], url_path="refresh-token")
    def refresh(self, request:Request):
        """Generate new access token using refresh token"""
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response({"error": "Refresh token is required."}, status=400)

        try:
            refresh = RefreshToken(refresh_token)
            new_access_token = str(refresh.access_token)
            return Response({"access": new_access_token}, status=200)

        except TokenError:
            return Response({"error": "Invalid or expired refresh token."}, status=401)
        

    @action(
        detail=False,
        methods=["post"],
        url_path="forget-password",
        permission_classes=[AllowAny],
        authentication_classes=[],
    )
    def forget_password(self, request:Request):
        """Send password reset link to user's email"""
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required."}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=404)

        # 🔑 ساختن توکن ساده (می‌تونی از jwt یا itsdangerous یا default_token_generator هم استفاده کنی)
        reset_token = get_random_string(length=32)
        user.password_reset_token = reset_token
        user.password_reset_expiry = now() + timedelta(hours=1)  # یک ساعت اعتبار
        user.save()

        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"

        # ارسال ایمیل
        html_content = render_to_string(
            "email/reset_password.html",
            {"reset_link": reset_link, "username": user.username},
        )

        email_msg = EmailMultiAlternatives(
            subject="🔑 Reset your CryptoZen password",
            body=f"Click here to reset your password: {reset_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email_msg.attach_alternative(html_content, "text/html")
        email_msg.send()

        return Response({"message": "Password reset link sent to your email."}, status=200)

    @action(
        detail=False,
        methods=["post"],
        url_path="reset-password/confirm",
        permission_classes=[AllowAny],
        authentication_classes=[],
    )
    def reset_password_confirm(self, request:Request):
        """
        Confirm password reset using token and set a new password.
        Expected payload: { "token": "...", "new_password": "..." }
        (اختیاری: "confirm_password")
        """
        token = request.data.get("token")
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")

        if not token or not new_password:
            return Response(
                {"error": "Token and new_password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if confirm_password is not None and new_password != confirm_password:
            return Response(
                {"error": "Passwords do not match."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(password_reset_token=token)
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not user.password_reset_expiry or now() > user.password_reset_expiry:
            # پاک‌سازی توکن منقضی
            user.password_reset_token = None
            user.password_reset_expiry = None
            user.save(update_fields=["password_reset_token", "password_reset_expiry"])
            return Response(
                {"error": "Token has expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # تنظیم پسورد جدید
        user.set_password(new_password)
        user.password_reset_token = None
        user.password_reset_expiry = None
        user.save()

        # (اختیاری) ایمیل اطلاع‌رسانی تغییر پسورد
        try:
            email_msg = EmailMultiAlternatives(
                subject="Your CryptoZen password was changed",
                body="Your password was successfully updated.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email] if user.email else [],
            )
            email_msg.send()
        except Exception:
            # در صورت خطای ایمیل، عملیات اصلی انجام شده—پس فقط ادامه بدهیم.
            pass

        return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)





@api_view(["GET"])
@permission_classes([AllowAny])
def confirm_verification_token(request:Request):
    token = request.query_params.get("token")
    if not token:
        return Response({"error": "Token not provided"}, status=400)

    try:
        user = User.objects.get(email_verification_token=token)
        user.is_verified = True
        user.awaiting_verification = False
        user.email_verification_token = None
        user.save()

        # Send confirmation VIP welcome email
        html_content = render_to_string(
            "email/confirm_verify.html",
            {
                "user_id": user.user_id,
                "user_name": user.username,
                "activation_code": user.user_id,
                "admin_username": "@cryptozen360",
                "website_url": "https://cryptozen360.com",
                "twitter_url": "https://x.com/cryptozen360",
                "support_email": "cryptozen360@gmail.com",
            },
        )

        email_msg = EmailMultiAlternatives(
            subject="🎉 Welcome to CryptoZen VIP – You're In!",
            body="You're now a VIP! Check your Telegram for access.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email_msg.attach_alternative(html_content, "text/html")

        # Embed logo in email
        logo_path = os.path.join(settings.BASE_DIR, "users/templates/email/logo.png")
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as f:
                logo = MIMEImage(f.read())
                logo.add_header("Content-ID", "<logo_image>")
                logo.add_header("Content-Disposition", "inline", filename="logo.png")
                email_msg.attach(logo)

        email_msg.send()

        return Response({"message": "Email verified successfully"})

    except User.DoesNotExist:
        return Response(
            {"error": "Invalid or expired verification token"},
            status=status.HTTP_400_BAD_REQUEST,
        )