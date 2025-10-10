from django.db import models
from users.models import User


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200, null=True, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    is_global = models.BooleanField(default=False)  # True = for all users
    show = models.BooleanField(default=True)

    def __str__(self):
        return self.title
