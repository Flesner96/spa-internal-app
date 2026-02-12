from django.urls import path
from . import views

urlpatterns = [   
    path("", views.notebook_view, name="notebook"), 
    path(
        "message/<int:pk>/edit/",
        views.edit_area_message,
        name="edit_area_message",
    ),
    path(
    "messages/<int:pk>/attachment/",
    views.download_area_message_attachment,
    name="download_area_message_attachment",
    ),
    path(
    "reply/<int:pk>/",
    views.reply_area_message,
    name="reply_message",
),

]
