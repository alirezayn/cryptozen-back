from django.contrib import admin

# Register your models here.
from .models import UserWallet,WithdrawRequests

admin.site.register(UserWallet)
admin.site.register(WithdrawRequests)
