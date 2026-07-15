from django import forms
from .models import Bike


class BikeForm(forms.ModelForm):
    class Meta:
        model = Bike
        fields = ["brand", "model", "year", "engine_cc", "registration_number", "fuel_type", "image"]
        widgets = {
            "registration_number": forms.TextInput(attrs={"placeholder": "e.g. MH12AB1234", "style": "text-transform:uppercase"}),
        }

    def clean_registration_number(self):
        return self.cleaned_data["registration_number"].upper().replace(" ", "")
