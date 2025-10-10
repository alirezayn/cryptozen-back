from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from django.utils.crypto import get_random_string


def user_profile_upload_path(instance, filename):
    return f"profile_images/{instance.user_id}/{filename}"


class User(AbstractUser):
    user_id = models.CharField(max_length=12, unique=True, editable=False)
    telegram_id = models.CharField(max_length=100, blank=True, null=True)
    profile_image = models.ImageField(
        upload_to=user_profile_upload_path, null=True, blank=True
    )
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=20, blank=True, null=True, unique=True)
    referral_link = models.URLField(blank=True, null=True)
    referred_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="referrals_list",
    )
    referrals = models.PositiveIntegerField(default=0)
    is_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=64, null=True, blank=True)
    awaiting_verification = models.BooleanField(default=False)
    password_reset_token = models.CharField(max_length=64, null=True, blank=True)
    password_reset_expiry = models.DateTimeField(null=True, blank=True)
    # New profile fields
    crypto_experience = models.CharField(
        max_length=20,
        choices=[
            ("beginner", "Beginner"),
            ("intermediate", "Intermediate"),
            ("advanced", "Advanced"),
        ],
        blank=True,
        null=True,
    )
    crypto_goal = models.CharField(
        max_length=50,
        choices=[
            ("learn_basics", "Learn & understand the basics"),
            ("long_term_portfolio", "Build a long-term portfolio"),
            ("signals_trading", "Get signals & trading strategies"),
            ("stay_updated", "Stay updated with the latest trends"),
            ("premium_community", "Join a premium community"),
        ],
        blank=True,
        null=True,
    )
    interests = models.JSONField(default=list, blank=True)  # For multi-select topics
    trading_platforms = models.JSONField(
        default=list, blank=True
    )  # For multi-select platforms
    monthly_budget = models.CharField(
        max_length=20,
        choices=[
            ("<100", "<$100"),
            ("100-500", "$100–$500"),
            ("500-1000", "$500–$1,000"),
            ("1000-5000", "$1,000–$5,000"),
            ("5000+", "$5,000+"),
        ],
        blank=True,
        null=True,
    )
    vip_interest = models.CharField(
        max_length=30,
        choices=[
            ("yes", "Yes, I want premium insights"),
            ("maybe", "Maybe, tell me more later"),
            ("no", "No, just free content for now"),
        ],
        blank=True,
        null=True,
    )
    learning_preference = models.CharField(
        max_length=30,
        choices=[
            ("short_videos", "Short videos"),
            ("articles", "Articles"),
            ("telegram_updates", "Telegram updates"),
            ("courses", "Courses"),
            ("mentorship", "1-on-1 mentorship"),
        ],
        blank=True,
        null=True,
    )
    crypto_years_active = models.CharField(
        max_length=20,
        choices=[
            ("<1", "Less than 1 year"),
            ("1-2", "1–2 years"),
            ("2-3", "2–3 years"),
            ("3-5", "3–5 years"),
            ("5+", "5+ years"),
        ],
        blank=True,
        null=True,
    )

    def save(self, *args, **kwargs):
        if not self.user_id:
            self.user_id = uuid.uuid4().hex[:5].upper()
        self.referral_link = f"https://cryptozen360.com/referral/{self.user_id}"
        super().save(*args, **kwargs)

    def generate_verification_token(self):
        self.email_verification_token = get_random_string(48)
        self.awaiting_verification = True  # set on token generation
        self.save()




