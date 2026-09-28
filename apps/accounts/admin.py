from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["username", "phone", "email", "is_staff", "date_joined"]
    search_fields = ["username", "phone", "email", "first_name", "last_name"]
    fieldsets = [
        *BaseUserAdmin.fieldsets,
        ("Liên hệ", {"fields": ["phone"]}),
    ]
