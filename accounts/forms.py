from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomerSignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=True)
    security_question = forms.ChoiceField(choices=User.SecurityQuestion.choices, label="Security question")
    security_answer = forms.CharField(max_length=100, label="Your answer", help_text="You'll need this to reset your password later.")

    class Meta:
        model = User
        fields = (
            "username", "first_name", "last_name", "email", "phone",
            "security_question", "security_answer", "password1", "password2",
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.CUSTOMER
        user.email = self.cleaned_data["email"]
        user.phone = self.cleaned_data["phone"]
        user.security_question = self.cleaned_data["security_question"]
        user.set_security_answer(self.cleaned_data["security_answer"])
        if commit:
            user.save()
        return user


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "phone", "profile_picture")


class IdentifyAccountForm(forms.Form):
    """Step 1 of password reset: find the account by username or email."""
    username_or_email = forms.CharField(label="Username or email")


class SecurityAnswerForm(forms.Form):
    """Step 2 of password reset: answer the account's security question."""
    answer = forms.CharField(max_length=100, label="Your answer")


class SetNewPasswordForm(forms.Form):
    password1 = forms.CharField(widget=forms.PasswordInput, label="New password")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm password")

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password1") != cleaned.get("password2"):
            raise forms.ValidationError("Passwords do not match.")
        if cleaned.get("password1") and len(cleaned["password1"]) < 8:
            raise forms.ValidationError("Password must be at least 8 characters.")
        return cleaned
