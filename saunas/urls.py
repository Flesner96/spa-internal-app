from django.urls import path
from . import views

urlpatterns = [
    path("", views.sauna_day_view, name="saunas"),
    path("session/<int:pk>/", views.sauna_session_detail, name="sauna_session_detail"),
    path("week/", views.sauna_week_view, name="sauna_week"),
]