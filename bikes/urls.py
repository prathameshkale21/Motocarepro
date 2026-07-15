from django.urls import path
from . import views

app_name = "bikes"

urlpatterns = [
    path("", views.bike_list, name="list"),
    path("add/", views.bike_add, name="add"),
    path("<int:pk>/edit/", views.bike_edit, name="edit"),
    path("<int:pk>/delete/", views.bike_delete, name="delete"),
]
