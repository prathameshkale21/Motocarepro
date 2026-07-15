from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.MotoCareLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", views.register, name="register"),
    path("profile/", views.profile, name="profile"),
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path("forgot-password/security-question/", views.security_question, name="security_question"),
    path("forgot-password/reset/", views.reset_password, name="reset_password"),
]
