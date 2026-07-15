from django.db.models import Count
from django.shortcuts import render
from django.utils import timezone

from appointments.models import Appointment
from mechanics.models import MechanicProfile
from reviews.models import Review
from services.models import ServiceCategory, ServicePackage


def landing(request):
    today = timezone.localdate()
    context = {
        "packages": ServicePackage.objects.all(),
        "categories": ServiceCategory.objects.prefetch_related("service_types"),
        "reviews": Review.objects.filter(is_published=True)[:6],
        "live_bookings_today": Appointment.objects.filter(date=today).exclude(status=Appointment.Status.CANCELLED).count(),
        "mechanic_count": MechanicProfile.objects.count(),
        "avg_rating": 4.8,
        "booking_steps": [
            "Date", "Time slot", "Service center", "Bike",
            "Service type", "Engine oil", "Pickup/Drop", "Payment",
        ],
    }
    return render(request, "pages/landing.html", context)


def about(request):
    return render(request, "pages/about.html")


def contact(request):
    return render(request, "pages/contact.html")


def faq(request):
    faqs = [
        {"q": "How do I cancel a booking?", "a": "Cancel from your dashboard up to 2 hours before your slot for a full refund."},
        {"q": "Can I bring my own engine oil?", "a": "Yes — select 'I will bring my own oil' during the oil step of booking."},
        {"q": "Do you offer pickup and drop?", "a": "Yes, for a flat ₹99 convenience fee within city limits."},
        {"q": "How do I track my service?", "a": "Your dashboard shows a live status timeline from Booked to Delivered."},
        {"q": "Is warranty included?", "a": "Every service package includes a written warranty period noted on your invoice."},
    ]
    return render(request, "pages/faq.html", {"faqs": faqs})
