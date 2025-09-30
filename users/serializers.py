from rest_framework import serializers
from .models import User


from rest_framework import serializers
from django.db import IntegrityError
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    referral_code = serializers.CharField(write_only=True, required=False)
    mobile = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "password",
            "telegram_id",
            "referral_link",
            "user_id",
            "profile_image",
            "first_name",
            "last_name",
            "mobile",
            "referral_code",
            "crypto_experience",
            "crypto_goal",
            "interests",
            "trading_platforms",
            "monthly_budget",
            "vip_interest",
            "learning_preference",
            "crypto_years_active",
        ]

    def validate(self, attrs):
        email = attrs.get("email")
        mobile = attrs.get("mobile")
        username = attrs.get("username")

        # Check for duplicates
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "Email already in use."})

        if User.objects.filter(mobile=mobile).exists():
            raise serializers.ValidationError(
                {"mobile": "Mobile number already in use."}
            )

        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({"username": "Username already taken."})

        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        referral_code = validated_data.pop("referral_code", None)

        user = User(**validated_data)
        user.set_password(password)

        # Handle collab logic
        if referral_code:
            try:
                referrer = User.objects.get(user_id=referral_code)
                user.referred_by = referrer
                referrer.referrals += 1
                referrer.save()
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    {"referral_code": "Invalid collab code."}
                )

        try:
            user.save()
        except IntegrityError as e:
            # Fallback for any race condition or missed check
            if "email" in str(e):
                raise serializers.ValidationError({"email": "Email already exists."})
            elif "mobile" in str(e):
                raise serializers.ValidationError(
                    {"mobile": "Mobile number already exists."}
                )
            elif "username" in str(e):
                raise serializers.ValidationError(
                    {"username": "Username already exists."}
                )
            else:
                raise serializers.ValidationError(
                    {"detail": "Something went wrong. Please try again."}
                )

        return user


class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "telegram_id",
            "referral_link",
            "user_id",
            "referrals",
            "profile_image",
            "full_name",
            "first_name",
            "last_name",
            "is_verified",
            "awaiting_verification",
            "crypto_experience",
            "crypto_goal",
            "interests",
            "trading_platforms",
            "monthly_budget",
            "vip_interest",
            "learning_preference",
            "crypto_years_active",
        ]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

    def get_profile_image(self, obj):
        request = self.context.get("request")
        if obj.profile_image and hasattr(obj.profile_image, "url"):
            return request.build_absolute_uri(obj.profile_image.url)
        return None


class VerificationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["is_verified", "awaiting_verification"]


from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        # Check if user exists
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError({"username": "User not found."})

        # Check password
        if not user.check_password(password):
            raise serializers.ValidationError({"password": "Incorrect password."})

        # Check if active
        if not user.is_active:
            raise serializers.ValidationError(
                {"non_field_errors": "This account is inactive."}
            )

        # All good: set self.user so super() works correctly
        self.user = user
        data = super().validate(attrs)

        # Add custom fields
        data["user_id"] = user.user_id
        data["email"] = user.email
        data["referral_link"] = user.referral_link

        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["user_id"] = user.user_id
        token["email"] = user.email
        token["referral_link"] = user.referral_link
        return token


class ProfileAnswersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "crypto_experience",
            "crypto_goal",
            "interests",
            "trading_platforms",
            "monthly_budget",
            "vip_interest",
            "learning_preference",
            "crypto_years_active",
        ]
