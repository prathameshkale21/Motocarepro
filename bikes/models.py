from django.db import models
from django.conf import settings


class Bike(models.Model):
    FUEL_CHOICES = [
        ("petrol", "Petrol"),
        ("electric", "Electric"),
        ("hybrid", "Hybrid"),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bikes"
    )
    brand = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.PositiveIntegerField()
    engine_cc = models.PositiveIntegerField(help_text="Engine capacity in cc")
    registration_number = models.CharField(max_length=20, unique=True)
    fuel_type = models.CharField(max_length=10, choices=FUEL_CHOICES, default="petrol")
    image = models.ImageField(upload_to="bikes/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.brand} {self.model} ({self.registration_number})"
