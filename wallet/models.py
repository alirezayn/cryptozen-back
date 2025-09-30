from django.db import models
from users.models import User


class UserWallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="wallet")
    balance = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - Balance: {self.balance}"



DESCRIPTION_MAP = {
    "pending": "If your request is not processed within 24 hours, please contact support.",
    "paid": "Your withdrawal has been successfully processed.",
    "rejected": "Your withdrawal request was rejected. Please contact support.",
}

class WithdrawRequests(models.Model):
    STATUS_CHOICES = [(k, k.capitalize()) for k in DESCRIPTION_MAP.keys()]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=8)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(choices=STATUS_CHOICES, default="pending", max_length=100)

    def save(self, *args, **kwargs):
        self.description = DESCRIPTION_MAP.get(self.status, "")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} - {self.amount} - {self.status}"