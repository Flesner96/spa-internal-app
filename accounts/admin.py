from django.contrib import admin
from .models import User, Area, Role, UserRole

admin.site.register(User)
admin.site.register(Area)
admin.site.register(Role)
admin.site.register(UserRole)