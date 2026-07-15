from django.contrib import admin
from .models import Bike


@admin.register(Bike)
class BikeAdmin(admin.ModelAdmin):
    list_display = ("brand", "model", "year", "engine_cc", "registration_number", "owner", "fuel_type")
    list_filter = ("brand", "fuel_type")
    search_fields = ("registration_number", "brand", "model", "owner__username")
