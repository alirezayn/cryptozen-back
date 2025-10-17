from django.db import models
from users.models import User
from datetime import date, timedelta


class Subscription(models.Model):
    PLAN_CHOICES = [
        ("basic", "Basic VIP Access"),
        ("quarterly", "Quarterly Plan"),
        ("six_month", "Six-Month Plan"),
        ("yearly", "Yearly Plan"),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField()
    active = models.BooleanField(default=True)
    cryptomus_recurring_uuid = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    want_to_upgrade = models.BooleanField(default=False)
    class Meta:
        ordering = ["-end_date"]
        verbose_name = "Subscription Plan"
        verbose_name_plural = "Subscription Plans"


class Payment(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
        ("partial", "Partial"),
    ]

    METHOD_CHOICES = [
        ("crypto", "Crypto"),
        ("card", "Card"),
        ("paypal", "PayPal"),
        ("bank", "Bank Transfer"),
        ("deposit", "Deposit"),
        ("withdraw", "Withdraw"),

    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subscription = models.ForeignKey(
        Subscription, on_delete=models.CASCADE, related_name="payments", null=True,blank=True
    )

    pre_subscription = models.CharField(max_length=100,blank=True,null=True)

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10)
    method = models.CharField(
        max_length=20, choices=METHOD_CHOICES, default="crypto"
    )  # ✅ NEW
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    cryptomus_payment_uuid = models.CharField(max_length=100, blank=True, null=True)
    payment_url = models.URLField(blank=True, null=True)
    payment_id = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def clean(self):
        if self.method != "deposit" and not self.subscription:
            raise ValueError("Subscription is required for non-deposit payments.")
    def __str__(self):
        return f"{self.user.username} - {self.amount} {self.currency} ({self.method})"


class PaymentHistory(models.Model):
    STATUS_CHOICES = [("success", "Success"), ("pending", "Pending")]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=50)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    date = models.DateTimeField(auto_now_add=True)


class SubscriptionPlan(models.Model):
    PLAN_CHOICES = [
        ("basic", "Basic VIP Access"),
        ("quarterly", "Quarterly Plan"),
        ("yearly", "Yearly Plan"),
        ("vip", "VIP Plan"),
    ]
    plan_type = models.CharField(max_length=20, choices=PLAN_CHOICES, unique=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    price_note = models.CharField(
        max_length=100, blank=True, null=True
    )  # like "(Save $15)"
    duration = models.CharField(max_length=50)  # e.g., "mo", "3 months", "year"
    months = models.PositiveIntegerField(default=1)
    features = models.TextField(help_text="Use comma-separated values")

    def feature_list(self):
        return [f.strip() for f in self.features.split(",") if f.strip()]

    def __str__(self):
        return self.title


class DiscountedPlan(models.Model):
    title = models.CharField(max_length=100)
    duration = models.CharField(max_length=50)  # e.g., "6-Month Plan"
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_note = models.CharField(max_length=100, blank=True, null=True)
    is_popular = models.BooleanField(default=False)
    highlight_text = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = "Discounted Plan"
        verbose_name_plural = "Discounted Plans"

    def __str__(self):
        return self.title
