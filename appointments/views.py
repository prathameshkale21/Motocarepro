from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from bikes.models import Bike
from mechanics.models import ServiceCenter, MechanicProfile
from services.models import ServiceType, EngineOil, Modification, ServicePackage

from .forms import (
    Step1DateSlotCenterForm, Step2BikeForm, Step3ServiceForm,
    Step4OilForm, Step5PickupForm, Step6PaymentForm, TrackBookingForm,
)
from .models import Appointment, Coupon

SESSION_KEY = "booking_wizard"


def build_status_timeline(appt):
    """Shared by the logged-in detail page and the public track-a-booking page."""
    try:
        current_index = Appointment.STATUS_FLOW.index(appt.status)
    except ValueError:
        current_index = -1  # cancelled or unknown status

    return [
        {
            "value": s,
            "label": s.replace("_", " ").title(),
            "done": current_index != -1 and i < current_index,
            "current": s == appt.status,
        }
        for i, s in enumerate(Appointment.STATUS_FLOW)
    ]


def _get_booked_slots(service_center_id, date):
    if not service_center_id or not date:
        return []
    return list(
        Appointment.objects.filter(service_center_id=service_center_id, date=date)
        .exclude(status=Appointment.Status.CANCELLED)
        .values_list("time_slot", flat=True)
    )


@login_required
def booking_start(request):
    request.session[SESSION_KEY] = {}
    return redirect("appointments:step1")


@login_required
def step1(request):
    data = request.session.get(SESSION_KEY, {})
    booked = _get_booked_slots(data.get("service_center"), data.get("date"))
    if request.method == "POST":
        form = Step1DateSlotCenterForm(request.POST, booked_slots=booked)
        if form.is_valid():
            data["date"] = form.cleaned_data["date"].isoformat()
            data["service_center"] = form.cleaned_data["service_center"].id
            data["time_slot"] = form.cleaned_data["time_slot"]
            request.session[SESSION_KEY] = data
            return redirect("appointments:step2")
    else:
        form = Step1DateSlotCenterForm(booked_slots=booked)
    return render(request, "appointments/step1.html", {"form": form, "step": 1})


@login_required
def step2(request):
    data = request.session.get(SESSION_KEY)
    if not data:
        return redirect("appointments:step1")
    if request.method == "POST":
        form = Step2BikeForm(request.POST, user=request.user)
        if form.is_valid():
            data["bike"] = form.cleaned_data["bike"].id
            request.session[SESSION_KEY] = data
            return redirect("appointments:step3")
    else:
        form = Step2BikeForm(user=request.user)
    has_bikes = Bike.objects.filter(owner=request.user).exists()
    return render(request, "appointments/step2.html", {"form": form, "step": 2, "has_bikes": has_bikes})


@login_required
def step3(request):
    data = request.session.get(SESSION_KEY)
    if not data:
        return redirect("appointments:step1")
    if request.method == "POST":
        form = Step3ServiceForm(request.POST)
        if form.is_valid():
            package = form.cleaned_data.get("package")
            data["package"] = package.id if package else None
            data["service_types"] = [s.id for s in form.cleaned_data.get("service_types", [])]
            data["modifications"] = [m.id for m in form.cleaned_data.get("modifications", [])]
            request.session[SESSION_KEY] = data
            return redirect("appointments:step4")
    else:
        form = Step3ServiceForm()
    return render(request, "appointments/step3.html", {"form": form, "step": 3})


@login_required
def step4(request):
    data = request.session.get(SESSION_KEY)
    if not data:
        return redirect("appointments:step1")
    if request.method == "POST":
        form = Step4OilForm(request.POST)
        if form.is_valid():
            data["bring_own_oil"] = form.cleaned_data["bring_own_oil"]
            oil = form.cleaned_data.get("engine_oil")
            data["engine_oil"] = oil.id if oil and not data["bring_own_oil"] else None
            request.session[SESSION_KEY] = data
            return redirect("appointments:step5")
    else:
        form = Step4OilForm()
    return render(request, "appointments/step4.html", {"form": form, "step": 4})


@login_required
def step5(request):
    data = request.session.get(SESSION_KEY)
    if not data:
        return redirect("appointments:step1")
    if request.method == "POST":
        form = Step5PickupForm(request.POST)
        if form.is_valid():
            data["pickup_option"] = form.cleaned_data["pickup_option"]
            data["pickup_address"] = form.cleaned_data["pickup_address"]
            request.session[SESSION_KEY] = data
            return redirect("appointments:step6")
    else:
        form = Step5PickupForm()
    return render(request, "appointments/step5.html", {"form": form, "step": 5})


def _calculate_total(data):
    subtotal = Decimal("0.00")
    if data.get("package"):
        subtotal += ServicePackage.objects.get(id=data["package"]).price
    for st in ServiceType.objects.filter(id__in=data.get("service_types", [])):
        subtotal += st.base_price
    for m in Modification.objects.filter(id__in=data.get("modifications", [])):
        subtotal += m.price
    if data.get("engine_oil") and not data.get("bring_own_oil"):
        oil = EngineOil.objects.filter(id=data["engine_oil"]).first()
        if oil:
            subtotal += oil.price_per_liter
    if data.get("pickup_option") == "pickup":
        subtotal += Decimal("99.00")
    return subtotal


@login_required
def step6(request):
    data = request.session.get(SESSION_KEY)
    if not data:
        return redirect("appointments:step1")
    subtotal = _calculate_total(data)
    code = (request.POST.get("coupon_code") or "").strip().upper() if request.method == "POST" else ""
    preview_discount = Decimal("0.00")
    if code:
        coupon = Coupon.objects.filter(code=code, is_active=True).first()
        if coupon:
            preview_discount = subtotal * Decimal(coupon.discount_percent) / Decimal("100")
    taxable_preview = subtotal - preview_discount
    gst_preview = (taxable_preview * Decimal("0.18")).quantize(Decimal("0.01"))

    if request.method == "POST":
        form = Step6PaymentForm(request.POST)
        if form.is_valid():
            discount = Decimal("0.00")
            code = form.cleaned_data.get("coupon_code")
            if code:
                coupon = Coupon.objects.filter(code=code, is_active=True).first()
                if coupon:
                    discount = subtotal * Decimal(coupon.discount_percent) / Decimal("100")

            taxable_value = subtotal - discount
            gst_rate = Decimal("18.00")
            cgst = (taxable_value * Decimal("0.09")).quantize(Decimal("0.01"))
            sgst = (taxable_value * Decimal("0.09")).quantize(Decimal("0.01"))
            total = taxable_value + cgst + sgst

            bike = get_object_or_404(Bike, id=data["bike"], owner=request.user)
            appt = Appointment.objects.create(
                customer=request.user,
                bike=bike,
                service_center_id=data["service_center"],
                date=data["date"],
                time_slot=data["time_slot"],
                package_id=data.get("package"),
                bring_own_oil=data.get("bring_own_oil", False),
                engine_oil_id=data.get("engine_oil"),
                pickup_option=data.get("pickup_option", Appointment.PickupOption.SELF_DROP),
                pickup_address=data.get("pickup_address", ""),
                subtotal=subtotal,
                coupon_code=code or "",
                discount=discount,
                gst_rate=gst_rate,
                cgst_amount=cgst,
                sgst_amount=sgst,
                total_amount=total,
                is_paid=(form.cleaned_data["pay_now"] == "online"),
            )
            appt.service_types.set(data.get("service_types", []))
            appt.modifications.set(data.get("modifications", []))
            del request.session[SESSION_KEY]
            messages.success(request, "Booking confirmed! Track your service status from your dashboard.")
            return redirect("appointments:confirmation", pk=appt.pk)
    else:
        form = Step6PaymentForm()
    return render(request, "appointments/step6.html", {
        "form": form, "step": 6, "subtotal": subtotal,
        "preview_discount": preview_discount, "taxable_preview": taxable_preview, "gst_preview": gst_preview,
        "total_preview": taxable_preview + gst_preview,
    })


@login_required
def invoice(request, pk):
    appt = get_object_or_404(Appointment, pk=pk)
    if not (appt.customer == request.user or request.user.is_admin_role()):
        messages.error(request, "You don't have access to that invoice.")
        return redirect("dashboard:redirect")

    line_items = []
    if appt.package:
        line_items.append({"name": f"{appt.package.get_tier_display()} Package", "qty": 1, "price": appt.package.price})
    for st in appt.service_types.all():
        line_items.append({"name": st.name, "qty": 1, "price": st.base_price})
    for m in appt.modifications.all():
        line_items.append({"name": m.name, "qty": 1, "price": m.price})
    if appt.engine_oil and not appt.bring_own_oil:
        line_items.append({"name": f"Engine Oil — {appt.engine_oil}", "qty": 1, "price": appt.engine_oil.price_per_liter})
    if appt.pickup_option == Appointment.PickupOption.PICKUP:
        line_items.append({"name": "Pickup & Drop Convenience Fee", "qty": 1, "price": Decimal("99.00")})

    return render(request, "appointments/invoice.html", {"appt": appt, "line_items": line_items})


@login_required
def confirmation(request, pk):
    appt = get_object_or_404(Appointment, pk=pk, customer=request.user)
    return render(request, "appointments/confirmation.html", {"appt": appt})


@login_required
def appointment_detail(request, pk):
    appt = get_object_or_404(Appointment, pk=pk)
    if not (appt.customer == request.user or request.user.is_admin_role() or
            (request.user.is_mechanic() and appt.mechanic and appt.mechanic.user == request.user)):
        messages.error(request, "You don't have access to that booking.")
        return redirect("dashboard:redirect")

    timeline = build_status_timeline(appt)
    return render(request, "appointments/detail.html", {"appt": appt, "timeline": timeline, "flow": Appointment.STATUS_FLOW})


@login_required
def update_status(request, pk):
    appt = get_object_or_404(Appointment, pk=pk)
    if not request.user.is_admin_role():
        messages.error(request, "Only admins can update job status.")
        return redirect("appointments:detail", pk=pk)
    if request.method == "POST":
        new_status = request.POST.get("status")
        notes = request.POST.get("notes", "")
        if new_status in Appointment.Status.values:
            appt.status = new_status
            if notes:
                appt.mechanic_notes = notes
            appt.save()
            messages.success(request, "Job status updated.")
    next_url = request.POST.get("next") or request.GET.get("next")
    if next_url:
        return redirect(next_url)
    return redirect("appointments:detail", pk=pk)


@login_required
def accept_appointment(request, pk):
    """Admin-only quick action: move a freshly booked appointment straight to Accepted."""
    appt = get_object_or_404(Appointment, pk=pk)
    if not request.user.is_admin_role():
        messages.error(request, "Only admins can accept a service booking.")
        return redirect("appointments:detail", pk=pk)
    if request.method == "POST":
        if appt.status == Appointment.Status.BOOKED:
            appt.status = Appointment.Status.ACCEPTED
            appt.save()
            messages.success(request, f"Booking #{appt.pk} accepted.")
        else:
            messages.info(request, f"Booking #{appt.pk} is already past the Booked stage.")
    next_url = request.POST.get("next") or request.GET.get("next")
    if next_url:
        return redirect(next_url)
    return redirect("appointments:detail", pk=pk)


@login_required
def claim_job(request, pk):
    """A mechanic assigns an unassigned appointment at their service center to themselves.
    This only assigns the job — moving it through Accepted → Delivered is an admin action."""
    if not request.user.is_mechanic():
        messages.error(request, "Only mechanics can claim jobs.")
        return redirect("dashboard:redirect")
    from mechanics.models import MechanicProfile
    profile, _ = MechanicProfile.objects.get_or_create(user=request.user)
    appt = get_object_or_404(Appointment, pk=pk, mechanic__isnull=True)
    if request.method == "POST":
        appt.mechanic = profile
        appt.save()
        messages.success(request, f"Job #{appt.pk} assigned to you. An admin will accept and move it forward.")
    return redirect("dashboard:mechanic")


def track_booking(request):
    """Public status check — no login required. A customer (or anyone who
    knows both the booking ID and the exact bike registration number) can
    verify a booking's live status without signing in."""
    result = None
    if request.method == "POST":
        form = TrackBookingForm(request.POST)
        if form.is_valid():
            appt = Appointment.objects.filter(
                pk=form.cleaned_data["booking_id"],
                bike__registration_number=form.cleaned_data["registration_number"],
            ).select_related("bike", "service_center", "mechanic__user").first()
            if appt:
                result = {"appt": appt, "timeline": build_status_timeline(appt)}
            else:
                messages.error(request, "No booking matches that ID and registration number. Double-check both and try again.")
    else:
        form = TrackBookingForm()
    return render(request, "appointments/track.html", {"form": form, "result": result})
