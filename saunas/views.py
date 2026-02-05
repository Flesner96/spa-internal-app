from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .forms import SaunaAttendanceForm
from .models import SaunaDay, SaunaSession
from accounts.models import Area
from datetime import timedelta
from django.utils.dateparse import parse_date
from .utils import get_week_range


@login_required
def sauna_day_view(request):
    user_area_code = request.user.area.code

    if user_area_code == "RC":
        target_area_code = "SA"
    else:
        target_area_code = user_area_code

    target_area = Area.objects.filter(code=target_area_code).first()

    if not target_area:
        return render(
            request,
            "saunas/day.html",
            {
                "sauna_day": None,
                "sessions": [],
            },
        )

    selected_date = request.GET.get("date")

    if selected_date:
        sauna_day = SaunaDay.objects.filter(
            area=target_area,
            date=selected_date,
        ).first()
    else:
        sauna_day = (
            SaunaDay.objects
            .filter(area=target_area)
            .order_by("-date")
            .first()
        )

    sessions = sauna_day.sessions.all() if sauna_day else []

    return render(
        request,
        "saunas/day.html",
        {
            "sauna_day": sauna_day,
            "sessions": sessions,
        },
    )


@login_required
def sauna_session_detail(request, pk):
    session = get_object_or_404(SaunaSession, pk=pk)
    if session.sauna_day.area != request.user.area and request.user.area.code != "SA":
        return redirect("saunas")

    user_area = request.user.area.code

    can_edit = user_area == "SA"

    if request.method == "POST" and can_edit:
        form = SaunaAttendanceForm(request.POST, instance=session)

        if form.is_valid():
            obj = form.save(commit=False)

            women = obj.women or 0
            men = obj.men or 0
            obj.total_people = women + men

            obj.save()

            return redirect("saunas")

    else:
        form = SaunaAttendanceForm(instance=session)

    return render(
        request,
        "saunas/session_detail.html",
        {
            "session": session,
            "form": form,
            "can_edit": can_edit,
        },
    )

@login_required
def sauna_week_view(request):
    user_area = request.user.area.code

    if user_area == "RC":
        target_area_code = "SA"
    else:
        target_area_code = user_area

    area = request.user.area.__class__.objects.get(code=target_area_code)

    selected = request.GET.get("date")
    base_date = parse_date(selected) if selected else None

    start, end = get_week_range(base_date)

    days = (
        SaunaDay.objects
        .filter(area=area, date__range=(start, end))
        .prefetch_related("sessions")
        .order_by("date")
    )

    # mapa: date → SaunaDay
    day_map = {d.date: d for d in days}

    week = []
    current = start

    while current <= end:
        week.append({
            "date": current,
            "day": day_map.get(current),
        })
        current += timedelta(days=1)

    return render(
        request,
        "saunas/week.html",
        {
            "week": week,
            "start": start,
            "end": end,
        },
    )