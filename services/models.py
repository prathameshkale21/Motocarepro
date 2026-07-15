from django.db import models


class ServiceCategory(models.Model):
    """General / Modification top-level grouping."""

    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Font Awesome class, e.g. fa-oil-can")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name_plural = "Service categories"

    def __str__(self):
        return self.name


class ServiceType(models.Model):
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name="service_types")
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    base_price = models.DecimalField(max_digits=8, decimal_places=2)
    duration_minutes = models.PositiveIntegerField(default=60)
    icon = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["category__order", "name"]

    def __str__(self):
        return self.name


class EngineOil(models.Model):
    OIL_TYPE_CHOICES = [
        ("synthetic", "Full Synthetic"),
        ("semi_synthetic", "Semi Synthetic"),
        ("mineral", "Mineral Oil"),
    ]

    brand = models.CharField(max_length=50)
    variant = models.CharField(max_length=80, blank=True)
    oil_type = models.CharField(max_length=20, choices=OIL_TYPE_CHOICES)
    price_per_liter = models.DecimalField(max_digits=7, decimal_places=2)
    is_genuine_brand = models.BooleanField(default=False, help_text="Manufacturer-genuine oil e.g. Honda/TVS/Bajaj Genuine")

    class Meta:
        ordering = ["brand"]

    def __str__(self):
        return f"{self.brand} {self.variant}".strip()


class Modification(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    icon = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class ServicePackage(models.Model):
    TIER_CHOICES = [
        ("silver", "Silver"),
        ("gold", "Gold"),
        ("platinum", "Platinum"),
        ("premium", "Premium"),
    ]

    tier = models.CharField(max_length=10, choices=TIER_CHOICES, unique=True)
    tagline = models.CharField(max_length=120, blank=True)
    services_included = models.ManyToManyField(ServiceType, related_name="packages", blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    duration_label = models.CharField(max_length=50, help_text="e.g. '90 minutes'")
    warranty_label = models.CharField(max_length=50, help_text="e.g. '30 days / 500 km'")
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ["price"]

    def __str__(self):
        return self.get_tier_display()
