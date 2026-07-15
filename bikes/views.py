from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .forms import BikeForm
from .models import Bike


@login_required
def bike_list(request):
    bikes = Bike.objects.filter(owner=request.user)
    return render(request, "bikes/bike_list.html", {"bikes": bikes})


@login_required
def bike_add(request):
    if request.method == "POST":
        form = BikeForm(request.POST, request.FILES)
        if form.is_valid():
            bike = form.save(commit=False)
            bike.owner = request.user
            bike.save()
            messages.success(request, f"{bike.brand} {bike.model} added to your garage.")
            return redirect("bikes:list")
    else:
        form = BikeForm()
    return render(request, "bikes/bike_form.html", {"form": form, "title": "Add a Bike"})


@login_required
def bike_edit(request, pk):
    bike = get_object_or_404(Bike, pk=pk, owner=request.user)
    if request.method == "POST":
        form = BikeForm(request.POST, request.FILES, instance=bike)
        if form.is_valid():
            form.save()
            messages.success(request, "Bike details updated.")
            return redirect("bikes:list")
    else:
        form = BikeForm(instance=bike)
    return render(request, "bikes/bike_form.html", {"form": form, "title": "Edit Bike"})


@login_required
def bike_delete(request, pk):
    bike = get_object_or_404(Bike, pk=pk, owner=request.user)
    if request.method == "POST":
        bike.delete()
        messages.info(request, "Bike removed from your garage.")
        return redirect("bikes:list")
    return render(request, "bikes/bike_confirm_delete.html", {"bike": bike})
