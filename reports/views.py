from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from accounts.permissions import Capability



@login_required
def reports_dashboard(request):

    if not request.user.can(Capability.VIEW_REPORTS):
        return HttpResponseForbidden()

    context = {
        "area": request.user.area
    }

    return render(
        request,
        "reports/reports_dashboard.html",
        context
    )