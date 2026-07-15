from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from services.models import ServiceCategory, ServiceType, EngineOil, Modification, ServicePackage
from mechanics.models import ServiceCenter, MechanicProfile
from appointments.models import Coupon

User = get_user_model()


class Command(BaseCommand):
    help = "Seed MotoCare Pro with demo service catalogue, service centers, a coupon, and a mechanic account."

    def handle(self, *args, **options):
        general, _ = ServiceCategory.objects.get_or_create(name="General Service", slug="general", defaults={"icon": "fa-oil-can", "order": 1})
        mod_cat, _ = ServiceCategory.objects.get_or_create(name="Modification", slug="modification", defaults={"icon": "fa-palette", "order": 2})

        service_defs = [
            (general, "General Service", "general-service", "Multi-point check, oil change, and chain lube.", 499, 60, "fa-oil-can"),
            (general, "Premium Service", "premium-service", "Deep clean plus full diagnostic scan.", 999, 90, "fa-star"),
            (general, "Water Wash", "water-wash", "Full exterior wash and dry.", 149, 20, "fa-droplet"),
            (general, "Chain Lubrication", "chain-lube", "Clean and lubricate the drive chain.", 199, 20, "fa-link"),
            (general, "Brake Service", "brake-service", "Pad inspection, adjustment, and bleed if needed.", 349, 40, "fa-hand"),
            (general, "Battery Replacement", "battery-replacement", "Swap in a fresh battery, old one recycled.", 1299, 20, "fa-car-battery"),
            (mod_cat, "Custom Painting", "custom-painting", "Full respray in a color of your choice.", 4999, 480, "fa-spray-can"),
            (mod_cat, "Performance Upgrade", "performance-upgrade", "ECU remap and exhaust tuning.", 3499, 180, "fa-gauge-high"),
            (mod_cat, "Ceramic Coating", "ceramic-coating", "Long-lasting protective ceramic layer.", 2999, 240, "fa-shield"),
            (mod_cat, "LED Lighting Upgrade", "led-lighting", "Swap to bright, efficient LED lighting.", 899, 60, "fa-lightbulb"),
        ]
        service_objs = {}
        for cat, name, slug, desc, price, dur, icon in service_defs:
            obj, _ = ServiceType.objects.get_or_create(
                slug=slug, defaults={"category": cat, "name": name, "description": desc, "base_price": price, "duration_minutes": dur, "icon": icon}
            )
            service_objs[slug] = obj

        oils = [
            ("Castrol", "Power1 Ultimate", "synthetic", 650, False),
            ("Motul", "300V", "synthetic", 890, False),
            ("Shell", "Advance Ultra", "synthetic", 720, False),
            ("Honda", "Genuine 10W30", "semi_synthetic", 480, True),
            ("TVS", "Genuine Oil", "mineral", 350, True),
        ]
        for brand, variant, oil_type, price, genuine in oils:
            EngineOil.objects.get_or_create(brand=brand, variant=variant, defaults={"oil_type": oil_type, "price_per_liter": price, "is_genuine_brand": genuine})

        mods = [
            ("Crash Guard", "Protective engine guard.", 1499),
            ("Alloy Wheels", "Lightweight alloy wheel set.", 8999),
            ("Exhaust", "Performance slip-on exhaust.", 4499),
            ("Seat Cover", "Weatherproof seat cover.", 599),
            ("Mobile Holder", "Handlebar phone mount.", 349),
        ]
        for name, desc, price in mods:
            Modification.objects.get_or_create(name=name, defaults={"description": desc, "price": price})

        packages = [
            ("silver", "The essentials, done right.", 799, "60 minutes", "15 days / 300 km", False, ["general-service", "water-wash"]),
            ("gold", "Our most-booked package.", 1499, "90 minutes", "30 days / 500 km", True, ["general-service", "premium-service", "chain-lube"]),
            ("platinum", "Deep service for high-mileage bikes.", 2499, "150 minutes", "45 days / 750 km", False, ["premium-service", "brake-service", "chain-lube"]),
            ("premium", "The full workshop treatment.", 3999, "180 minutes", "60 days / 1000 km", False, ["premium-service", "brake-service", "battery-replacement", "chain-lube"]),
        ]
        for tier, tagline, price, dur, warranty, featured, service_slugs in packages:
            pkg, _ = ServicePackage.objects.get_or_create(tier=tier, defaults={"tagline": tagline, "price": price, "duration_label": dur, "warranty_label": warranty, "is_featured": featured})
            pkg.services_included.set([service_objs[s] for s in service_slugs])

        center, _ = ServiceCenter.objects.get_or_create(
            name="MotoCare Pro - Hinjewadi", defaults={"address": "Plot 12, Hinjewadi Phase 1", "city": "Pune", "phone": "+911234567890"}
        )
        ServiceCenter.objects.get_or_create(
            name="MotoCare Pro - Kothrud", defaults={"address": "Karve Road", "city": "Pune", "phone": "+911234567891"}
        )

        Coupon.objects.get_or_create(code="WELCOME10", defaults={"discount_percent": 10})

        if not User.objects.filter(username="mechanic_demo").exists():
            m = User.objects.create_user(username="mechanic_demo", password="MotoCare@123", role=User.Role.MECHANIC, first_name="Ravi", email="ravi@motocarepro.example")
            m.security_question = User.SecurityQuestion.BIKE
            m.set_security_answer("Bajaj")
            m.save()
            MechanicProfile.objects.get_or_create(user=m, defaults={"service_center": center, "specialization": "Engine & brakes", "years_experience": 6})

        self.stdout.write(self.style.SUCCESS("Demo data seeded. Mechanic login: mechanic_demo / MotoCare@123"))
