from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import UserCreateForm
from .permissions import require_role
from django.contrib.auth.decorators import login_required
from .models import User


def root_redirect(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return redirect("login")


@login_required
def dashboard_view(request):
    user = request.user

    roles = set(
        user.userrole_set.values_list("role__code", flat=True)
    )

    context = {
        "roles": roles,
        "area": user.area,
    }

    return render(request, "accounts/dashboard.html", context)

