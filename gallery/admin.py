from django.contrib import admin
from .models import GalleryImage, IntroductionContent

admin.site.register(GalleryImage)
@admin.register(IntroductionContent)
class IntroductionContentAdmin(admin.ModelAdmin):
    list_display = ['title']