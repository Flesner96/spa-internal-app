from django.contrib import admin
from .models import SaunaDay, SaunaSession


class SaunaSessionInline(admin.TabularInline):
    model = SaunaSession
    extra = 1


@admin.register(SaunaDay)
class SaunaDayAdmin(admin.ModelAdmin):
    list_display = ("area", "date")
    inlines = [SaunaSessionInline]


@admin.register(SaunaSession)
class SaunaSessionAdmin(admin.ModelAdmin):
    list_display = (
        "sauna_day",
        "sauna_name",
        "start_time",
        "leader_name",
        "total_people",
    )
