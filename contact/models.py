from django.db import models


class ContactMessage(models.Model):
    CHOICES = [
        ("withdraw","Withdraw"),
        ("contact","Contact")
    ]

    message_type = models.CharField(max_length=150,choices=CHOICES,default="contact")
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} ({self.email})"


def comment_image_upload_path(instance, filename):
    return f"user_comments/{instance.name.replace(' ', '_')}/{filename}"


class UserComment(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(
        upload_to=comment_image_upload_path, null=True, blank=True
    )
    rating = models.DecimalField(max_digits=2, decimal_places=1)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.rating}"
