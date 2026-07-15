from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

from bikes.models import Bike
from mechanics.models import ServiceCenter, MechanicProfile
from services.models import ServiceType, EngineOil, Modification, ServicePackage


def generate_time_slots():
    """09:00 to 18:30 in 30 minute increments, used as fixture data / choices helper."""
    slots = []
    start = timezone.datetime.combine(timezone.datetime.today(), timezone.datetime.min.time()) + timedelta(hours=9)
    end = start + timedelta(hours=9, minutes=30)
    current = start
    while current <= end:
        slots.append(current.strftime("%I:%M %p"))
        current += timedelta(minutes=30)
    return slots


class Appointment(models.Model):
    class Status(models.TextChoices):
        BOOKED = "booked", "Booked"
        ACCEPTED = "accepted", "Accepted"
        PICKED = "picked", "Bike Picked"
        INSPECTION = "inspection", "Inspection"
        REPAIR = "repair", "Repair Started"
        WAITING_PARTS = "waiting_parts", "Waiting for Parts"
        TESTING = "testing", "Testing"
        COMPLETED = "completed", "Completed"
        READY = "ready", "Ready for Delivery"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"

    STATUS_FLOW = [
        Status.BOOKED, Status.ACCEPTED, Status.PICKED, Status.INSPECTION,
        Status.REPAIR, Status.WAITING_PARTS, Status.TESTING, Status.COMPLETED,
        Status.READY, Status.DELIVERED,
    ]

    class PickupOption(models.TextChoices):
        SELF_DROP = "self_drop", "I will drop off my bike"
        PICKUP = "pickup", "Pick up from my location"

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="appointments"
    )
    bike = models.ForeignKey(Bike, on_delete=models.CASCADE, related_name="appointments")
    service_center = models.ForeignKey(ServiceCenter, on_delete=models.PROTECT, related_name="appointments")
    mechanic = models.ForeignKey(
        MechanicProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_jobs"
    )

    service_types = models.ManyToManyField(ServiceType, blank=True, related_name="appointments")
    package = models.ForeignKey(ServicePackage, on_delete=models.SET_NULL, null=True, blank=True, related_name="appointments")
    modifications = models.ManyToManyField(Modification, blank=True, related_name="appointments")
    engine_oil = models.ForeignKey(EngineOil, on_delete=models.SET_NULL, null=True, blank=True)
    bring_own_oil = models.BooleanField(default=False)

    date = models.DateField()
    time_slot = models.CharField(max_length=20)  # e.g. "09:30 AM"
    pickup_option = models.CharField(max_length=12, choices=PickupOption.choices, default=PickupOption.SELF_DROP)
    pickup_address = models.CharField(max_length=255, blank=True)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.BOOKED)
    mechanic_notes = models.TextField(blank=True)

    subtotal = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    coupon_code = models.CharField(max_length=20, blank=True)
    discount = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    gst_rate = models.DecimalField(max_digits=4, decimal_places=2, default=18.00, help_text="Total GST %, split evenly as CGST + SGST")
    cgst_amount = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    sgst_amount = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    is_paid = models.BooleanField(default=False)
    payment_reference = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-time_slot"]
        unique_together = ("service_center", "date", "time_slot", "mechanic")

    def status_progress_percent(self):
        if self.status == self.Status.CANCELLED:
            return 0
        try:
            idx = self.STATUS_FLOW.index(self.status)
            return int((idx / (len(self.STATUS_FLOW) - 1)) * 100)
        except ValueError:
            return 0

    @property
    def taxable_value(self):
        return self.subtotal - self.discount

    @property
    def invoice_number(self):
        return f"MC-INV-{self.created_at.year if self.created_at else ''}-{self.pk:06d}"

    def __str__(self):
        return f"Appointment #{self.pk} - {self.bike} on {self.date} {self.time_slot}"


class AppointmentImage(models.Model):
    """Photos attached to an appointment: customer problem photos, or
    admin/mechanic uploaded before/after service photos."""

    class Kind(models.TextChoices):
        BIKE_PHOTO = "bike", "Bike Photo"
        PROBLEM_PHOTO = "problem", "Problem Photo"
        BEFORE = "before", "Before Service"
        AFTER = "after", "After Service"

    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="appointments/")
    kind = models.CharField(max_length=10, choices=Kind.choices)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_kind_display()} for Appointment #{self.appointment_id}"


class Coupon(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount_percent = models.PositiveIntegerField(default=10)
    is_active = models.BooleanField(default=True)
    valid_until = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.code
