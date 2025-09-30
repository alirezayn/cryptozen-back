from rest_framework import viewsets, permissions
from collab.models import CollabLink
from .models import User
from .serializers import (
    UserSerializer,
    UserProfileSerializer,
    CustomTokenObtainPairSerializer,
    VerificationStatusSerializer,
    ProfileAnswersSerializer,
)
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
            print(sub)
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
    def signup(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            referral_id = request.data.get("referral_id")
            if referral_id:
                try:
                    link = CollabLink.objects.get(collab_id=referral_id)
                    link.join_users.add(user)
                    link.save()
                except CollabLink.DoesNotExist:
                    pass

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["put"], url_path="update-profile")
    def update_profile(self, request):
        user = request.user

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
        return Response({"message": "Profile updated"})

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

    @action(
        detail=False,
        methods=["get"],
        url_path=r"verify/confirm/(?P<token>[^/.]+)",
        permission_classes=[AllowAny],
    )
    def confirm_verification(self, request, token=None):
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
                    "activation_code": user.user_id,  # you can generate real code here
                    "admin_username": "@cryptozen360",  # change this
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

            # Embed logo
            logo_path = os.path.join(
                settings.BASE_DIR, "users/templates/email/logo.png"
            )
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
    def confirm_verification(self, request):
        """this function is check code as send by user , find user by its email."""

        email = request.data.get("email")
        code = request.data.get("code")

        if not email or not code:
            return Response({"error": "Email and code are required."}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=404)

        if str(user.user_id) != str(code):
            return Response({"error": "Invalid verification code."}, status=400)

        user.is_verified = True
        user.awaiting_verification = True
        user.save()

        return Response({"message": "Email verified successfully."}, status=200)

    @action(detail=False, methods=["post"], url_path="check/info", permission_classes=[permissions.AllowAny],
            authentication_classes=[])
    def check_information(self, request):
        """Check username & password validity"""
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"error": "Username and password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)
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
