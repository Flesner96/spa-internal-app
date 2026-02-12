from django.urls import path
from .views import balance_view

urlpatterns = [
    path("", balance_view, name="balance"),
]
