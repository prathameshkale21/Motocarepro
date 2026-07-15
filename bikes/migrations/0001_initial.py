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
            name="Bike",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("brand", models.CharField(max_length=50)),
                ("model", models.CharField(max_length=50)),
                ("year", models.PositiveIntegerField()),
                ("engine_cc", models.PositiveIntegerField(help_text="Engine capacity in cc")),
                ("registration_number", models.CharField(max_length=20, unique=True)),
                ("fuel_type", models.CharField(choices=[("petrol", "Petrol"), ("electric", "Electric"), ("hybrid", "Hybrid")], default="petrol", max_length=10)),
                ("image", models.ImageField(blank=True, null=True, upload_to="bikes/")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="bikes", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
