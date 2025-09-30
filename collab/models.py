from django.db import models
from django.conf import settings
from django.utils.crypto import get_random_string


class CollabLink(models.Model):
    """this model is creat collab link"""
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="referral_data")
    url = models.URLField(unique=True, null=True, blank=True)
    collab_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    join_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="join_users")
    cost_from_join_users = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Collab of {self.owner.email}"

    def generate_url(self):
        """this method generate url by random string"""
        base_url = "https://back.cryptozen360.com/collab/invite/"
        unique_id = get_random_string(length=50)
        while CollabLink.objects.filter(url=base_url + unique_id).exists():
            unique_id = get_random_string(length=50)
        return f"{base_url}{unique_id}"

    def save(self, *args, **kwargs):
        """url fill auto"""
        if self.url is None:
            self.url = self.generate_url()
            self.collab_id = self.url.split("/")[len(self.url.split("/")) - 1]
        super(CollabLink, self).save(*args, **kwargs)
