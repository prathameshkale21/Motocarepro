from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("customer", "rating", "would_recommend", "is_published", "created_at")
    list_filter = ("rating", "is_published", "would_recommend")
