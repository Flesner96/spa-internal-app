from django.urls import path
from .views import balance_view, balance_history_view

urlpatterns = [
    path("", balance_view, name="balance"),
    path("history/", balance_history_view, name="balance_history"),

]
