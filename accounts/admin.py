from django.contrib import admin
from .models import User, Area, Role, UserRole, AreaMessage

admin.site.register(User)
admin.site.register(Area)
admin.site.register(Role)
admin.site.register(UserRole)

@admin.register(AreaMessage)
class AreaMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "area", "author", "created_at")
    list_filter = ("area",)
    search_fields = ("content", "author__email")