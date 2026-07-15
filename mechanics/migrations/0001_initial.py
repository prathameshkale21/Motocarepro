import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ServiceCenter",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("address", models.CharField(max_length=255)),
                ("city", models.CharField(max_length=50)),
                ("latitude", models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ("longitude", models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ("phone", models.CharField(blank=True, max_length=15)),
                ("opening_time", models.TimeField(default="09:00")),
                ("closing_time", models.TimeField(default="18:30")),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="MechanicProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("specialization", models.CharField(blank=True, help_text="e.g. Engine repair, Modifications", max_length=120)),
                ("years_experience", models.PositiveIntegerField(default=0)),
                ("rating", models.DecimalField(decimal_places=2, default=5.0, max_digits=3)),
                ("is_available", models.BooleanField(default=True)),
                ("service_center", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="mechanics", to="mechanics.servicecenter")),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="mechanic_profile", to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
