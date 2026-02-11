from django.urls import path
from .views import schedule_view, combined_view


urlpatterns = [
    path("", schedule_view, name="classes"),
    path("combined/", combined_view, name="classes_combined"),
]
