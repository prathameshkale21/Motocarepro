from django.db import models
from django.conf import settings


class ServiceCenter(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=50)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True)
    opening_time = models.TimeField(default="09:00")
    closing_time = models.TimeField(default="18:30")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} - {self.city}"


class MechanicProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="mechanic_profile"
    )
    service_center = models.ForeignKey(
        ServiceCenter, on_delete=models.SET_NULL, null=True, blank=True, related_name="mechanics"
    )
    specialization = models.CharField(max_length=120, blank=True, help_text="e.g. Engine repair, Modifications")
    years_experience = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.0)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"Mechanic: {self.user.get_full_name() or self.user.username}"
