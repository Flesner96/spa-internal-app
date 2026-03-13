from django.shortcuts import render
from ..core.services.sheets import get_schedule
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

@login_required
def schedule_view(request):

    area = request.user.area.code

    if area == "RC":
        return reception_schedule(request)

    if area == "SA":
        return sauna_schedule(request)

    if area == "SP":
        return spa_schedule(request)

    if area == "BD":
        return manager_schedule(request)

    return HttpResponseForbidden()



def reception_schedule(request):

    schedule = get_schedule("RC")

    return render(
        request,
        "schedule/reception_schedule.html",
        {"schedule": schedule}
    )

def sauna_schedule(request):

    return render(
        request,
        "schedule/sauna_schedule.html"
    )


def spa_schedule(request):

    return render(
        request,
        "schedule/spa_schedule.html"
    )


def manager_schedule(request):

    return render(
        request,
        "schedule/manager_schedule.html"
    )