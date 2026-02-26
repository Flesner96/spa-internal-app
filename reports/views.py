from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from accounts.permissions import Capability



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
        "reports/dashboard.html",
        {
            "note": note,
            "can_edit_note": can_edit,
        },
    )