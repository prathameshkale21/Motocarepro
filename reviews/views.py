from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from appointments.models import Appointment
from .forms import ReviewForm
from .models import Review


@login_required
def add_review(request, appointment_pk):
    appt = get_object_or_404(Appointment, pk=appointment_pk, customer=request.user)
    if appt.status != Appointment.Status.DELIVERED:
        messages.error(request, "You can review a service once it's been delivered.")
        return redirect("appointments:detail", pk=appt.pk)
    if hasattr(appt, "review"):
        messages.info(request, "You've already reviewed this service.")
        return redirect("appointments:detail", pk=appt.pk)

    if request.method == "POST":
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.appointment = appt
            review.customer = request.user
            review.save()
            request.user.reward_points += 20
            request.user.save(update_fields=["reward_points"])
            messages.success(request, "Thanks for the review! +20 reward points.")
            return redirect("appointments:detail", pk=appt.pk)
    else:
        form = ReviewForm()
    return render(request, "reviews/review_form.html", {"form": form, "appt": appt})
