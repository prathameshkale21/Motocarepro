import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("accounts", "0001_initial"),
        ("bikes", "0001_initial"),
        ("mechanics", "0001_initial"),
        ("services", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Coupon",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(max_length=20, unique=True)),
                ("discount_percent", models.PositiveIntegerField(default=10)),
                ("is_active", models.BooleanField(default=True)),
                ("valid_until", models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="Appointment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("bring_own_oil", models.BooleanField(default=False)),
                ("date", models.DateField()),
                ("time_slot", models.CharField(max_length=20)),
                ("pickup_option", models.CharField(choices=[("self_drop", "I will drop off my bike"), ("pickup", "Pick up from my location")], default="self_drop", max_length=12)),
                ("pickup_address", models.CharField(blank=True, max_length=255)),
                ("status", models.CharField(choices=[("booked", "Booked"), ("accepted", "Accepted"), ("picked", "Bike Picked"), ("inspection", "Inspection"), ("repair", "Repair Started"), ("waiting_parts", "Waiting for Parts"), ("testing", "Testing"), ("completed", "Completed"), ("ready", "Ready for Delivery"), ("delivered", "Delivered"), ("cancelled", "Cancelled")], default="booked", max_length=20)),
                ("mechanic_notes", models.TextField(blank=True)),
                ("subtotal", models.DecimalField(decimal_places=2, default=0, max_digits=9)),
                ("coupon_code", models.CharField(blank=True, max_length=20)),
                ("discount", models.DecimalField(decimal_places=2, default=0, max_digits=9)),
                ("total_amount", models.DecimalField(decimal_places=2, default=0, max_digits=9)),
                ("is_paid", models.BooleanField(default=False)),
                ("payment_reference", models.CharField(blank=True, max_length=100)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("bike", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="appointments", to="bikes.bike")),
                ("customer", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="appointments", to=settings.AUTH_USER_MODEL)),
                ("engine_oil", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="services.engineoil")),
                ("mechanic", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="assigned_jobs", to="mechanics.mechanicprofile")),
                ("modifications", models.ManyToManyField(blank=True, related_name="appointments", to="services.modification")),
                ("package", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="appointments", to="services.servicepackage")),
                ("service_center", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="appointments", to="mechanics.servicecenter")),
                ("service_types", models.ManyToManyField(blank=True, related_name="appointments", to="services.servicetype")),
            ],
            options={
                "ordering": ["-date", "-time_slot"],
                "unique_together": {("service_center", "date", "time_slot", "mechanic")},
            },
        ),
        migrations.CreateModel(
            name="AppointmentImage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("image", models.ImageField(upload_to="appointments/")),
                ("kind", models.CharField(choices=[("bike", "Bike Photo"), ("problem", "Problem Photo"), ("before", "Before Service"), ("after", "After Service")], max_length=10)),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                ("appointment", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="images", to="appointments.appointment")),
            ],
        ),
    ]
