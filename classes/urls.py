from django.urls import path
from .views import schedule_view, combined_view, manage_create, manage_list, manage_edit, manage_delete


urlpatterns = [
    path("", schedule_view, name="classes"),
    path("combined/", combined_view, name="classes_combined"),
    path("manage/", manage_list, name="classes_manage"),
    path("manage/new/", manage_create, name="classes_create"),
    path("manage/<int:pk>/edit/", manage_edit, name="classes_edit"),
    path("manage/<int:pk>/delete/", manage_delete, name="classes_delete"),

]
