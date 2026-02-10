from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import PoolEvent
from .utils import generate_hour_slots, build_hour_grid
from accounts.permissions import Capability
from django.http import HttpResponseForbidden

@login_required
def schedule_view(request):
    if not request.user.can(Capability.VIEW_CLASSES):
        return HttpResponseForbidden()

    event_type = request.GET.get("type", "CL")

    events = PoolEvent.objects.filter(event_type=event_type)

    hour_slots = generate_hour_slots()

    DAY_NAMES = [
    "Poniedziałek",
    "Wtorek",
    "Środa",
    "Czwartek",
    "Piątek",
    "Sobota",
    "Niedziela",
    ]

    week = []
    

    for day in range(7):
        day_events = events.filter(day_of_week=day)

        week.append({
            "index": day,
            "name": DAY_NAMES[day],
            "grid": build_hour_grid(day_events, hour_slots),
        })
    
    return render(
        request,
        "classes/schedule.html",
        {
            "week": week,
            "time_slots": hour_slots,
            "event_type": event_type,
        },
    )




