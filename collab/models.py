from django.db import models
from django.conf import settings
from django.utils.crypto import get_random_string



def generate_referral_code():
    return get_random_string(length=10)

class CollabLink(models.Model):
    """This model represents a referral/collaboration link"""
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="referral_data"
    )
    collab_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    join_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="joined_collabs",
        blank=True
    )
    cost_from_join_users = models.PositiveIntegerField(default=20)
    created_at = models.DateTimeField(auto_now_add=True)
    code = models.CharField(max_length=10, default=generate_referral_code)
    reward = models.PositiveIntegerField(default=0)
    pro_cost_available = models.BooleanField(default=False)
    def __str__(self):
        return f"Collab of {self.owner.email}"

    def generate_collab_id(self):
        """Generate unique random collab_id"""
        unique_id = get_random_string(length=50)
        while CollabLink.objects.filter(collab_id=unique_id).exists():
            unique_id = get_random_string(length=50)
        return unique_id

    def save(self, *args, **kwargs):
        """Automatically assign a unique collab_id if not set"""
        if not self.collab_id:
            self.collab_id = self.generate_collab_id()
        super().save(*args, **kwargs)

    @property
    def url(self):
        """Return dynamic referral URL without storing it"""
        base_url = f"{settings.FRONTEND_URL}/referral/{self.owner.user_id}/"
        return f"{base_url}"
