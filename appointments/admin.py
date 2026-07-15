from django.contrib import admin
from .models import Appointment, AppointmentImage, Coupon


class AppointmentImageInline(admin.TabularInline):
    model = AppointmentImage
    extra = 0


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "bike", "service_center", "date", "time_slot", "status", "total_amount", "is_paid")
    list_filter = ("status", "service_center", "date", "is_paid")
    search_fields = ("customer__username", "bike__registration_number")
    inlines = [AppointmentImageInline]
    filter_horizontal = ("service_types", "modifications")


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ("code", "discount_percent", "is_active", "valid_until")
