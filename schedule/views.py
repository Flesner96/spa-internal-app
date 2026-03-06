from django.shortcuts import render
from .services import get_schedule


def reception_schedule(request):

    schedule = get_schedule()

    return render(
        request,
        "schedule/reception_schedule.html",
        {"schedule": schedule}
    )