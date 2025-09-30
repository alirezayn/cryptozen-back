from django.db import models

def gallery_image_upload_path(instance, filename):
    return f'gallery_images/{filename}'

class GalleryImage(models.Model):
    image = models.ImageField(upload_to=gallery_image_upload_path)
    caption = models.CharField(max_length=255, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.caption or f"Image {self.pk}"

class IntroductionContent(models.Model):
    title = models.CharField(max_length=200, default="What is CryptoZen?")
    video = models.FileField(upload_to="introduction/videos/")
    poster_desktop = models.ImageField(upload_to="introduction/posters/desktop/")
    poster_mobile = models.ImageField(upload_to="introduction/posters/mobile/")
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Introduction Section Content"
        verbose_name_plural = "Introduction Section Contents"

    def __str__(self):
        return self.title