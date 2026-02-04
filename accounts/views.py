from django.shortcuts import render, redirect
from .forms import UserProfileForm
from django.contrib.auth.decorators import login_required
from .models import User


def root_view(request):
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


@login_required
def profile_view(request):
    user = request.user

    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = UserProfileForm(instance=user)

    return render(
        request,
        "accounts/profile.html",
        {"form": form}
    )