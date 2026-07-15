from datetime import timedelta, datetime

from django import forms
from django.utils import timezone

from bikes.models import Bike
from mechanics.models import ServiceCenter
from services.models import ServiceType, EngineOil, Modification, ServicePackage
from .models import Appointment, Coupon


def all_time_slots():
    slots = []
    current = datetime.combine(datetime.today(), datetime.min.time()) + timedelta(hours=9)
    end = datetime.combine(datetime.today(), datetime.min.time()) + timedelta(hours=18, minutes=30)
    while current <= end:
        slots.append(current.strftime("%I:%M %p"))
        current += timedelta(minutes=30)
    return slots


class Step1DateSlotCenterForm(forms.Form):
    date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    service_center = forms.ModelChoiceField(queryset=ServiceCenter.objects.filter(is_active=True))
    time_slot = forms.ChoiceField(choices=[])

    def __init__(self, *args, **kwargs):
        booked_slots = kwargs.pop("booked_slots", [])
        super().__init__(*args, **kwargs)
        available = [s for s in all_time_slots() if s not in booked_slots]
        self.fields["time_slot"].choices = [(s, s) for s in available]

    def clean_date(self):
        date = self.cleaned_data["date"]
        if date < timezone.localdate():
            raise forms.ValidationError("Please choose a current or future date.")
        return date


class Step2BikeForm(forms.Form):
    bike = forms.ModelChoiceField(queryset=Bike.objects.none())

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.fields["bike"].queryset = Bike.objects.filter(owner=user)


class PricedModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    """Renders each checkbox label as 'Name — ₹price' instead of just the name."""

    def label_from_instance(self, obj):
        price = getattr(obj, "base_price", None)
        if price is None:
            price = getattr(obj, "price", None)
        if price is not None:
            return f"{obj.name} — ₹{price}"
        return str(obj)


class Step3ServiceForm(forms.Form):
    package = forms.ModelChoiceField(queryset=ServicePackage.objects.all(), required=False, empty_label="Build my own (à la carte)")
    service_types = PricedModelMultipleChoiceField(
        queryset=ServiceType.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    modifications = PricedModelMultipleChoiceField(
        queryset=Modification.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )


class PricedModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj} — ₹{obj.price_per_liter}/L"


class Step4OilForm(forms.Form):
    bring_own_oil = forms.BooleanField(required=False, label="I will bring my own oil")
    engine_oil = PricedModelChoiceField(queryset=EngineOil.objects.all(), required=False)


class Step5PickupForm(forms.Form):
    pickup_option = forms.ChoiceField(choices=Appointment.PickupOption.choices, widget=forms.RadioSelect)
    pickup_address = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 2}))


class Step6PaymentForm(forms.Form):
    coupon_code = forms.CharField(required=False)
    pay_now = forms.ChoiceField(
        choices=[("online", "Pay online now"), ("service_center", "Pay at service center")],
        widget=forms.RadioSelect,
        initial="service_center",
    )

    def clean_coupon_code(self):
        code = self.cleaned_data.get("coupon_code", "").strip().upper()
        if code:
            if not Coupon.objects.filter(code=code, is_active=True).exists():
                raise forms.ValidationError("This coupon code is invalid or expired.")
        return code


class TrackBookingForm(forms.Form):
    """Public, no-login status check. Requires the booking ID *and* the bike's
    registration number together, so a booking can't be looked up by ID alone."""
    booking_id = forms.IntegerField(label="Booking ID", min_value=1, widget=forms.NumberInput(attrs={"placeholder": "e.g. 104"}))
    registration_number = forms.CharField(label="Bike registration number", widget=forms.TextInput(attrs={"placeholder": "e.g. MH12AB1234"}))

    def clean_registration_number(self):
        return self.cleaned_data["registration_number"].upper().replace(" ", "")
