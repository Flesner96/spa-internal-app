from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from accounts.permissions import Capability
from .forms import ShiftCloseReportForm
from django.utils import timezone
from decimal import Decimal

@login_required
def reports_dashboard(request):

    if not request.user.can(Capability.VIEW_REPORTS):
        return HttpResponseForbidden()

    from .models import ShiftHandoverNote

    note, _ = ShiftHandoverNote.objects.get_or_create(
        area=request.user.area
    )

    can_edit = (
        request.user.has_role("BS")
        and request.user.area == note.area
    ) or request.user.is_sys_admin

    if request.method == "POST" and can_edit:
        note.content = request.POST.get("content", "")
        note.updated_by = request.user
        note.save()

    return render(
        request,
        "reports/reports_dashboard.html",
        {
            "note": note,
            "can_edit_note": can_edit,
        },
    )


@login_required
def shift_close_form(request):

    if not request.user.can(Capability.VIEW_REPORTS):
        return HttpResponseForbidden()

    prefill_cash = request.GET.get("prefill")

    if request.method == "POST":
        form = ShiftCloseReportForm(request.POST)

        if form.is_valid():
            report = form.save(commit=False)
            report.area = request.user.area
            report.created_by = request.user
            report.shift_date = timezone.localdate()

            if prefill_cash:
                report.auto_prefilled = True
                report.closing_cash = Decimal(prefill_cash)

            report.save()

            return redirect("reports:reports_dashboard")

    else:
        form = ShiftCloseReportForm(prefill_cash=prefill_cash)

    return render(
        request,
        "reports/shift_close_form.html",
        {"form": form}
    )