from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.redirect_by_role, name="redirect"),
    path("customer/", views.customer_dashboard, name="customer"),
    path("mechanic/", views.mechanic_dashboard, name="mechanic"),
    path("admin/", views.admin_dashboard, name="admin"),
    path("admin/appointments/", views.admin_appointments, name="admin_appointments"),
]
