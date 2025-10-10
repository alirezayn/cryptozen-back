from django.db import models


class Question(models.Model):
    QUESTION_TYPES = (
        ("normal", "Normal"),
        ("vip", "VIP"),
    )

    number = models.CharField(max_length=5)
    text = models.CharField(max_length=255)
    answer = models.TextField()
    type = models.CharField(max_length=10, choices=QUESTION_TYPES, default="normal")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.number} - {self.text[:40]}"
