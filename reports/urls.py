from django.urls import path
from . import views

app_name = "reports"

urlpatterns = [
    path("", views.reports_dashboard, name="reports_dashboard"),
    path("shift-close/", views.shift_close_form, name="shift_close_form"),
]