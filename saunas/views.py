from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .forms import SaunaAttendanceForm
from .models import SaunaDay, SaunaSession
from accounts.models import Area



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