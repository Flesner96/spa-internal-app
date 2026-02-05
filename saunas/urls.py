from django.urls import path
from . import views

urlpatterns = [
    path("", views.sauna_day_view, name="saunas"),
]