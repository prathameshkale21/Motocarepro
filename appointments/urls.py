from django.urls import path
from . import views

app_name = "appointments"

urlpatterns = [
    path("track/", views.track_booking, name="track"),
    path("book/", views.booking_start, name="start"),
    path("book/date-slot/", views.step1, name="step1"),
    path("book/bike/", views.step2, name="step2"),
    path("book/services/", views.step3, name="step3"),
    path("book/oil/", views.step4, name="step4"),
    path("book/pickup/", views.step5, name="step5"),
    path("book/payment/", views.step6, name="step6"),
    path("<int:pk>/confirmation/", views.confirmation, name="confirmation"),
    path("<int:pk>/invoice/", views.invoice, name="invoice"),
    path("<int:pk>/", views.appointment_detail, name="detail"),
    path("<int:pk>/accept/", views.accept_appointment, name="accept"),
    path("<int:pk>/update-status/", views.update_status, name="update_status"),
    path("<int:pk>/claim/", views.claim_job, name="claim_job"),
]
