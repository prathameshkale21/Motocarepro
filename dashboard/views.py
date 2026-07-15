import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Q
from django.shortcuts import render, redirect
from django.utils import timezone

from appointments.models import Appointment
from bikes.models import Bike
from mechanics.models import MechanicProfile
from reviews.models import Review


@login_required
def redirect_by_role(request):
    user = request.user
    if user.is_mechanic():
        return redirect("dashboard:mechanic")
    if user.is_admin_role():
        return redirect("dashboard:admin")
    return redirect("dashboard:customer")


@login_required
def customer_dashboard(request):
    appointments = Appointment.objects.filter(customer=request.user)
    upcoming = appointments.exclude(
        status__in=[Appointment.Status.DELIVERED, Appointment.Status.CANCELLED]
    ).order_by("date", "time_slot").first()
    latest_booking = appointments.order_by("-created_at").first()
    history = appointments.filter(
        status__in=[Appointment.Status.DELIVERED, Appointment.Status.CANCELLED]
    )[:10]
    bikes = Bike.objects.filter(owner=request.user)
    context = {
        "upcoming": upcoming,
        "latest_booking": latest_booking,
        "history": history,
        "bikes": bikes,
        "bike_count": bikes.count(),
        "total_services": appointments.filter(status=Appointment.Status.DELIVERED).count(),
    }
    return render(request, "dashboard/customer.html", context)


@login_required
def mechanic_dashboard(request):
    profile, _ = MechanicProfile.objects.get_or_create(user=request.user)
    today = timezone.localdate()
    jobs = Appointment.objects.filter(mechanic=profile)
    todays_jobs = jobs.filter(date=today).exclude(status=Appointment.Status.CANCELLED)
    pending = jobs.exclude(status__in=[Appointment.Status.DELIVERED, Appointment.Status.CANCELLED])
    completed = jobs.filter(status=Appointment.Status.DELIVERED)
    unassigned = Appointment.objects.filter(
        mechanic__isnull=True, service_center=profile.service_center
    ).exclude(status=Appointment.Status.CANCELLED) if profile.service_center else Appointment.objects.none()
    context = {
        "profile": profile,
        "todays_jobs": todays_jobs,
        "pending": pending,
        "completed_count": completed.count(),
        "unassigned": unassigned,
        "status_choices": Appointment.STATUS_FLOW,
    }
    return render(request, "dashboard/mechanic.html", context)


@login_required
def admin_dashboard(request):
    if not request.user.is_admin_role():
        return redirect("dashboard:redirect")

    appointments = Appointment.objects.all()
    today = timezone.localdate()
    month_start = today.replace(day=1)

    total_revenue = appointments.filter(is_paid=True).aggregate(v=Sum("total_amount"))["v"] or 0
    todays_earnings = appointments.filter(is_paid=True, date=today).aggregate(v=Sum("total_amount"))["v"] or 0
    monthly_bookings = appointments.filter(date__gte=month_start).count()

    status_breakdown = appointments.values("status").annotate(count=Count("id")).order_by("-count")

    from accounts.models import User
    total_customers = User.objects.filter(role=User.Role.CUSTOMER).count()
    total_mechanics = User.objects.filter(role=User.Role.MECHANIC).count()

    top_services = (
        appointments.values("service_types__name")
        .filter(service_types__isnull=False)
        .annotate(count=Count("id"))
        .order_by("-count")[:5]
    )

    cancelled = appointments.filter(status=Appointment.Status.CANCELLED).count()

    context = {
        "total_revenue": total_revenue,
        "todays_earnings": todays_earnings,
        "monthly_bookings": monthly_bookings,
        "total_customers": total_customers,
        "total_mechanics": total_mechanics,
        "cancelled": cancelled,
        "status_labels": json.dumps([s["status"] for s in status_breakdown]),
        "status_counts": json.dumps([s["count"] for s in status_breakdown]),
        "top_services": top_services,
        "recent_activity": appointments.order_by("-updated_at")[:8],
        "recent_reviews": Review.objects.filter(is_published=True)[:5],
    }
    return render(request, "dashboard/admin.html", context)


@login_required
def admin_appointments(request):
    """Admin-only: full appointment list with quick Accept + status-update actions."""
    if not request.user.is_admin_role():
        messages.error(request, "Only admins can manage bookings from here.")
        return redirect("dashboard:redirect")

    appointments = Appointment.objects.select_related(
        "customer", "bike", "service_center", "mechanic__user"
    ).order_by("-date", "-time_slot")

    status_filter = request.GET.get("status", "")
    if status_filter in Appointment.Status.values:
        appointments = appointments.filter(status=status_filter)

    context = {
        "appointments": appointments[:100],
        "status_choices": Appointment.Status.choices,
        "flow": Appointment.STATUS_FLOW,
        "active_filter": status_filter,
    }
    return render(request, "dashboard/admin_appointments.html", context)
