from django.contrib import admin
from .models import ServiceCategory, ServiceType, EngineOil, Modification, ServicePackage


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "order")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "base_price", "duration_minutes", "is_active")
    list_filter = ("category", "is_active")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(EngineOil)
class EngineOilAdmin(admin.ModelAdmin):
    list_display = ("brand", "variant", "oil_type", "price_per_liter", "is_genuine_brand")
    list_filter = ("oil_type", "is_genuine_brand")


@admin.register(Modification)
class ModificationAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "is_active")


@admin.register(ServicePackage)
class ServicePackageAdmin(admin.ModelAdmin):
    list_display = ("tier", "price", "duration_label", "warranty_label", "is_featured")
    filter_horizontal = ("services_included",)
