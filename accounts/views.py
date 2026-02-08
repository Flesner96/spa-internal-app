from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import UserProfileForm


def root_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return redirect("login")


@login_required
def dashboard_view(request):
    area_code = request.user.area.code  # np. "RECEPTION", "SPA", "MANAGER"

    tools_by_area = {
        "RC": [
            {
                "name": "Zeszyt",
                "icon": "bi-journal-text",
                "url": "notebook",
                "enabled": True,
            },
            {
                "name": "Grafik",
                "icon": "bi-calendar-week",
                "url": "schedule",
                "enabled": False,
            },
            {
                "name": "Vouchery",
                "icon": "bi-card-list",
                "url": "voucher",
                "enabled": False,
            },
            {
                "name": "Stan gotówki",
                "icon": "bi-currency-exchange",
                "url": "balance",
                "enabled": False,
            },
            {
                "name": "Formularze",
                "icon": "bi-ui-checks",
                "url": "forms",
                "enabled": False,
            },
            {
                "name": "Raporty",
                "icon": "bi-graph-up",
                "url": "reports",
                "enabled": False,
            },
            {
                "name": "Seanse saunowe",
                "icon": "bi-thermometer-half",
                "url": "saunas",
                "enabled": True,
            },
            {
                "name": "Zajęcia",
                "icon": "bi-person-arms-up",
                "url": "classes",
                "enabled": False,
            },
        ],
        "SP": [
            {
                "name": "Zeszyt",
                "icon": "bi-journal-text",
                "url": "notebook",
                "enabled": True,
            },
            
        ],
        "SA": [
            {
                "name": "Zeszyt",
                "icon": "bi-journal-text",
                "url": "notebook",
                "enabled": True,
            },
            {
                "name": "Grafik",
                "icon": "bi-calendar-week",
                "url": "schedule",
                "enabled": False,
            },
            {
                "name": "Formularze",
                "icon": "bi-ui-checks",
                "url": "forms",
                "enabled": False,
            },
            {
                "name": "Seanse saunowe",
                "icon": "bi-thermometer-half",
                "url": "saunas",
                "enabled": True,
            },
        ],
        "BD": [
            {
                "name": "Zeszyt",
                "icon": "bi-journal-text",
                "url": "notebook",
                "enabled": True,
            },
            {
                "name": "Grafik",
                "icon": "bi-calendar-week",
                "url": "schedule",
                "enabled": False,
            },
            {
                "name": "Raporty",
                "icon": "bi-graph-up",
                "url": "reports",
                "enabled": False,
            },
        ],
    }

    tools = tools_by_area.get(area_code, [])

    return render(
        request,
        "accounts/dashboard.html",
        {
            "tools": tools
        }
    )


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


