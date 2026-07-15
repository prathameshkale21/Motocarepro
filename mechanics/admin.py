from django.contrib import admin
from .models import ServiceCenter, MechanicProfile


@admin.register(ServiceCenter)
class ServiceCenterAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "phone", "opening_time", "closing_time", "is_active")


@admin.register(MechanicProfile)
class MechanicProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "service_center", "specialization", "years_experience", "rating", "is_available")
    list_filter = ("service_center", "is_available")
