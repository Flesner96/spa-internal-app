from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from core.rbac.permissions import Capability
from core.rbac.decorators import require_capability
from .forms import ShiftCloseReportForm
from django.utils import timezone
from decimal import Decimal
from .models import ShiftCloseReport

@login_required
@require_capability(Capability.VIEW_REPORTS)
def reports_dashboard(request):

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
@require_capability(Capability.CREATE_SHIFT_REPORT)
def shift_close_form(request):

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

@login_required
@require_capability(Capability.VIEW_SHIFT_REPORT_LIST)
def shift_report_list(request):

    reports = ShiftCloseReport.objects.filter(
        area=request.user.area
    ).select_related("created_by").order_by(
        "-shift_date",
        "-created_at"
    )

    return render(
        request,
        "reports/shift_report_list.html",
        {"reports": reports},
    )


@login_required
@require_capability(Capability.VIEW_SHIFT_REPORT_DETAIL)
def shift_report_detail(request, report_id):
    
    report = get_object_or_404(
        ShiftCloseReport,
        id=report_id,
        area=request.user.area
    )

    return render(
        request,
        "reports/shift_report_detail.html",
        {"report": report},
    )


@login_required
@require_capability(Capability.COMPARE_SHIFT_REPORTS)
def compare_shift_reports(request):
    
    ids = request.GET.getlist("ids")
    
    if len(ids) != 2:
        return HttpResponseBadRequest("Wybierz dokładnie 2 raporty")

    reports = (
        ShiftCloseReport.objects
        .filter(id__in=ids)
        .select_related("created_by")
        .order_by("created_at")
    )

    if reports.count() != 2:
        return HttpResponseBadRequest("Nie znaleziono raportów")

    r1, r2 = reports

    return render(
        request,
        "reports/shift_report_compare.html",
        {
            "r1": r1,
            "r2": r2,
        },
    )