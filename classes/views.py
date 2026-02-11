from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import PoolEvent
from .utils import generate_hour_slots, build_hour_grid, build_lane_conflict_grid
from accounts.permissions import Capability
from django.http import HttpResponseForbidden
from datetime import date



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

DAY_NAMES = [
    "Poniedziałek",
    "Wtorek",
    "Środa",
    "Czwartek",
    "Piątek",
    "Sobota",
    "Niedziela",
    ]

@login_required
def combined_view(request):
    if not request.user.can(Capability.VIEW_CLASSES):
        return HttpResponseForbidden()

    day = int(request.GET.get("day", date.today().weekday()))
    day = max(0, min(day, 6))  # clamp safety

    prev_day = (day - 1) % 7
    next_day = (day + 1) % 7

    events = PoolEvent.objects.filter(day_of_week=day)

    hour_slots = generate_hour_slots()
    grid = build_lane_conflict_grid(events, hour_slots)

    return render(
        request,
        "classes/combined.html",
        {
            "grid": grid,
            "hour_slots": hour_slots,
            "day": day,
            "day_name": DAY_NAMES[day],
            "day_names": DAY_NAMES,
            "prev_day": prev_day,
            "next_day": next_day,
        },
    )

