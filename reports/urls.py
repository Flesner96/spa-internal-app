from django.urls import path
from . import views

app_name = "reports"

urlpatterns = [
    path("", views.reports_dashboard, name="reports_dashboard"),
    path("shift-close/", views.shift_close_form, name="shift_close_form"),
    path(
    "shift-reports/",
    views.shift_report_list,
    name="shift_report_list",
    ),
    path(
    "shift-reports/<int:report_id>/",
    views.shift_report_detail,
    name="shift_report_detail",
    ),
    path(
    "shift-reports/compare/",
    views.compare_shift_reports,
    name="compare_shift_reports",
    ),
]