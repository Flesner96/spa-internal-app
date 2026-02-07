from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .forms import SaunaAttendanceForm
from .models import SaunaDay, SaunaSession
from accounts.models import Area
from datetime import timedelta, datetime
from django.utils.dateparse import parse_date
from .utils import get_week_range, parse_polish_day_month
from django.contrib import messages
from .parser import parse_sauna_text, split_description_and_sauna


@login_required
def sauna_day_view(request, date):
    user_area_code = request.user.area.code

    # mapowanie RC → SA
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

    selected_date = parse_date(date)

    if not selected_date:
        return render(
            request,
            "saunas/day.html",
            {
                "sauna_day": None,
                "sessions": [],
            },
        )

    sauna_day = SaunaDay.objects.filter(
        area=target_area,
        date=selected_date,
    ).first()

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

    # blokada cross-area
    if (
        session.sauna_day.area != request.user.area
        and request.user.area.code != "SA"
    ):
        return redirect("saunas")

    user_area = request.user.area.code

    # 🔥 TU BYŁ BUG
    can_edit = (
        user_area == "SA"
        and session.sauna_day.is_editable()
    )

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

@login_required
def sauna_import_view(request):

    preview = request.session.get("sauna_import_preview")
    if request.user.area.code != "SA":
        messages.error(request, "Brak uprawnień do importu seansów.")
        return redirect("saunas")
    if request.method == "POST":

        action = request.POST.get("action")

        # =====================
        # 1. PREVIEW
        # =====================
        if action == "preview":

            raw_text = request.POST.get("raw_text", "")
            parsed = parse_sauna_text(raw_text)

            request.session["sauna_import_preview"] = parsed

            return redirect("sauna_import")

        # =====================
        # 2. SAVE
        # =====================
        if action == "save" and preview:

            parsed_date = parse_polish_day_month(preview.get("date"))

            if not parsed_date:
                messages.error(
                    request,
                    "Nie udało się odczytać daty z importu."
                )
                return redirect("sauna_import")

            target_area = Area.objects.get(code="SA")

            sauna_day, _ = SaunaDay.objects.get_or_create(
                area=target_area,
                date=parsed_date,
            )

            # nadpisujemy plan dnia
            sauna_day.sessions.all().delete()

            for item in preview["sessions"]:

                try:
                    start_time = datetime.strptime(
                        item["time"],
                        "%H:%M"
                    ).time()
                except Exception:
                    continue  # pomiń zepsuty wpis

                start_dt = datetime.strptime(item["time"], "%H:%M")
                end_dt = start_dt + timedelta(minutes=15)

                start_time = start_dt.time()
                end_time = end_dt.time()

                desc, sauna = split_description_and_sauna(item["description"])

                SaunaSession.objects.create(
                    sauna_day=sauna_day,
                    session_name=desc,
                    start_time=start_time,
                    end_time=end_time,
                    sauna_name=sauna,
                    leader_name=preview.get("leader", ""),
                    created_by=request.user,
                )

            request.session.pop("sauna_import_preview", None)

            messages.success(request, "Import zapisany.")

            return redirect("saunas")

    return render(
        request,
        "saunas/import.html",
        {
            "preview": preview,
        },
    )