from datetime import date

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import SaunaDay


@login_required
def sauna_day_view(request):
    area = request.user.area

    selected_date = request.GET.get("date")

    if selected_date:
        sauna_day = SaunaDay.objects.filter(
            area=area,
            date=selected_date
        ).first()
    else:
        sauna_day = SaunaDay.objects.filter(
            area=area
        ).order_by("-date").first()

    sessions = sauna_day.sessions.all() if sauna_day else []

    return render(
        request,
        "saunas/day.html",
        {
            "sauna_day": sauna_day,
            "sessions": sessions,
        },
    )
