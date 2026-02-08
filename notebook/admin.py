from django.contrib import admin
from .views import AreaMessage

@admin.register(AreaMessage)
class AreaMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "area", "author", "created_at")
    list_filter = ("area",)
    search_fields = ("content", "author__email")