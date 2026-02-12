from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .forms import SaunaAttendanceForm, ParsedSessionFormSet
from .models import SaunaDay, SaunaSession
from accounts.models import Area
from datetime import timedelta, datetime, date
from django.utils.dateparse import parse_date
from .utils import get_week_range, parse_polish_day_month
from django.contrib import messages
from .parser import parse_sauna_text, split_description_and_sauna
from django.http import HttpResponseForbidden
from accounts.permissions import Capability


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
    
    if (
        session.sauna_day.area != request.user.area
        and not request.user.can(Capability.VIEW_SAUNAS)
):
        return HttpResponseForbidden()



    can_edit = (
        request.user.can(Capability.EDIT_SAUNA_ATTENDANCE)
        and request.user.area.code == "SA"
        and session.sauna_day.is_editable()
    )



    if request.method == "POST":
        if not can_edit:
            return HttpResponseForbidden()

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

    prev_week = start - timedelta(days=7)
    next_week = start + timedelta(days=7)

    return render(
        request,
        "saunas/week.html",
        {
            "week": week,
            "start": start,
            "end": end,
            "prev_week": prev_week,
            "next_week": next_week,
        },
    )

@login_required
def sauna_import_view(request):

    if not request.user.can(Capability.IMPORT_SAUNAS):
        return HttpResponseForbidden()


    meta = request.session.get("sauna_import_meta")

    if request.method == "POST":

        action = request.POST.get("action")

        # ===== PREVIEW =====
        if action == "preview":

            raw_text = request.POST.get("raw_text", "")
            parsed = parse_sauna_text(raw_text)

            initial = []

            for s in parsed["sessions"]:
                name, sauna = split_description_and_sauna(s["description"])

                initial.append({
                    "start_time": s["time"],
                    "session_name": name,
                    "sauna_name": sauna,
                })

            formset = ParsedSessionFormSet(initial=initial)

            request.session["sauna_import_meta"] = {
                "date": parsed["date"],
                "leader": parsed["leader"],
            }

            return render(
                request,
                "saunas/import.html",
                {
                    "formset": formset,
                    "meta": request.session["sauna_import_meta"],
                },
            )

        # ===== SAVE =====
        if action == "save":

            formset = ParsedSessionFormSet(request.POST)

            if formset.is_valid() and meta:

                normalized_date = parse_polish_day_month(meta["date"])

                if not normalized_date:
                    messages.error(request, "Nieprawidłowa data w imporcie.")
                    return redirect("sauna_import")

                sauna_day, _ = SaunaDay.objects.get_or_create(
                    area=request.user.area,
                    date=normalized_date,
                )

                sauna_day.sessions.all().delete()

                for form in formset:
                    data = form.cleaned_data

                    start = data["start_time"]

                    end = (
                        datetime.combine(date.today(), start)
                        + timedelta(minutes=15)
                    ).time()

                    SaunaSession.objects.create(
                        sauna_day=sauna_day,
                        session_name=data["session_name"],
                        sauna_name=data["sauna_name"],
                        leader_name=meta["leader"],
                        start_time=start,
                        end_time=end,
                        created_by=request.user,
                    )

                request.session.pop("sauna_import_meta", None)

                messages.success(request, "Import zapisany.")
                return redirect("saunas")

    return render(
        request,
        "saunas/import.html",
        {
            "formset": None,
            "meta": meta,
        },
    )
