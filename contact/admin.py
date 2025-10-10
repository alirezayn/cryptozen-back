from django.contrib import admin
from .models import ContactMessage, UserComment

admin.site.register(ContactMessage)
admin.site.register(UserComment)
