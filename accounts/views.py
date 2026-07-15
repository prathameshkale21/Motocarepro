from django.contrib import messages
from django.contrib.auth import login, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db.models import Q
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from .forms import (
    CustomerSignUpForm, ProfileUpdateForm,
    IdentifyAccountForm, SecurityAnswerForm, SetNewPasswordForm,
)

User = get_user_model()


class MotoCareLoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True


def register(request):
    if request.method == "POST":
        form = CustomerSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to MotoCare Pro, {user.first_name or user.username}!")
            return redirect("dashboard:redirect")
    else:
        form = CustomerSignUpForm()
    return render(request, "accounts/register.html", {"form": form})


@login_required
def profile(request):
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("accounts:profile")
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, "accounts/profile.html", {"form": form})


# --------------------------------------------------------------------------
# Forgot password: 3-step flow using a security question instead of email OTP
#   Step 1: identify the account (username or email)
#   Step 2: answer that account's security question
#   Step 3: set a new password
# --------------------------------------------------------------------------

def forgot_password(request):
    """Step 1: find the account."""
    if request.method == "POST":
        form = IdentifyAccountForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data["username_or_email"].strip()
            user = User.objects.filter(Q(username__iexact=identifier) | Q(email__iexact=identifier)).first()
            if user:
                request.session["reset_user_id"] = user.id
                return redirect("accounts:security_question")
            messages.error(request, "No account found with that username or email.")
    else:
        form = IdentifyAccountForm()
    return render(request, "accounts/forgot_password.html", {"form": form})


def security_question(request):
    """Step 2: answer the security question tied to the account."""
    user_id = request.session.get("reset_user_id")
    if not user_id:
        return redirect("accounts:forgot_password")
    user = User.objects.filter(id=user_id).first()
    if not user:
        return redirect("accounts:forgot_password")

    if request.method == "POST":
        form = SecurityAnswerForm(request.POST)
        if form.is_valid():
            if user.check_security_answer(form.cleaned_data["answer"]):
                request.session["reset_verified"] = True
                return redirect("accounts:reset_password")
            messages.error(request, "That answer doesn't match our records. Please try again.")
    else:
        form = SecurityAnswerForm()

    return render(request, "accounts/security_question.html", {
        "form": form,
        "question_label": user.get_security_question_display(),
    })


def reset_password(request):
    """Step 3: set a new password, only reachable after a verified answer."""
    user_id = request.session.get("reset_user_id")
    if not user_id or not request.session.get("reset_verified"):
        return redirect("accounts:forgot_password")

    if request.method == "POST":
        form = SetNewPasswordForm(request.POST)
        if form.is_valid():
            user = User.objects.get(id=user_id)
            user.set_password(form.cleaned_data["password1"])
            user.save()
            del request.session["reset_user_id"]
            del request.session["reset_verified"]
            messages.success(request, "Password reset successfully. Please log in.")
            return redirect("accounts:login")
    else:
        form = SetNewPasswordForm()
    return render(request, "accounts/reset_password.html", {"form": form})
