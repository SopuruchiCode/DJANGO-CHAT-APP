from django.contrib import admin
from .models import CustomUser,Account

# Register your models here.

admin.site.register(CustomUser)
admin.site.register(Account)