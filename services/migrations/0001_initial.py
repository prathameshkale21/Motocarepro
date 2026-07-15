import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ServiceCategory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=50, unique=True)),
                ("slug", models.SlugField(unique=True)),
                ("icon", models.CharField(blank=True, help_text="Font Awesome class, e.g. fa-oil-can", max_length=50)),
                ("order", models.PositiveIntegerField(default=0)),
            ],
            options={
                "verbose_name_plural": "Service categories",
                "ordering": ["order"],
            },
        ),
        migrations.CreateModel(
            name="EngineOil",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("brand", models.CharField(max_length=50)),
                ("variant", models.CharField(blank=True, max_length=80)),
                ("oil_type", models.CharField(choices=[("synthetic", "Full Synthetic"), ("semi_synthetic", "Semi Synthetic"), ("mineral", "Mineral Oil")], max_length=20)),
                ("price_per_liter", models.DecimalField(decimal_places=2, max_digits=7)),
                ("is_genuine_brand", models.BooleanField(default=False, help_text="Manufacturer-genuine oil e.g. Honda/TVS/Bajaj Genuine")),
            ],
            options={
                "ordering": ["brand"],
            },
        ),
        migrations.CreateModel(
            name="Modification",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True)),
                ("price", models.DecimalField(decimal_places=2, max_digits=8)),
                ("icon", models.CharField(blank=True, max_length=50)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="ServiceType",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("slug", models.SlugField(unique=True)),
                ("description", models.TextField(blank=True)),
                ("base_price", models.DecimalField(decimal_places=2, max_digits=8)),
                ("duration_minutes", models.PositiveIntegerField(default=60)),
                ("icon", models.CharField(blank=True, max_length=50)),
                ("is_active", models.BooleanField(default=True)),
                ("category", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="service_types", to="services.servicecategory")),
            ],
            options={
                "ordering": ["category__order", "name"],
            },
        ),
        migrations.CreateModel(
            name="ServicePackage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("tier", models.CharField(choices=[("silver", "Silver"), ("gold", "Gold"), ("platinum", "Platinum"), ("premium", "Premium")], max_length=10, unique=True)),
                ("tagline", models.CharField(blank=True, max_length=120)),
                ("price", models.DecimalField(decimal_places=2, max_digits=8)),
                ("duration_label", models.CharField(help_text="e.g. '90 minutes'", max_length=50)),
                ("warranty_label", models.CharField(help_text="e.g. '30 days / 500 km'", max_length=50)),
                ("is_featured", models.BooleanField(default=False)),
                ("services_included", models.ManyToManyField(blank=True, related_name="packages", to="services.servicetype")),
            ],
            options={
                "ordering": ["price"],
            },
        ),
    ]
