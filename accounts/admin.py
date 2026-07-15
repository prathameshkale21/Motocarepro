from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "role", "phone", "reward_points", "is_active")
    list_filter = ("role", "is_active")
    fieldsets = UserAdmin.fieldsets + (
        ("MotoCare Pro Profile", {
            "fields": ("role", "phone", "profile_picture", "reward_points", "referral_code")
        }),
        ("Security Question", {
            "fields": ("security_question", "security_answer"),
            "description": "security_answer is stored hashed and cannot be viewed in plain text.",
        }),
    )
