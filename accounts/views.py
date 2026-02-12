from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import UserProfileForm
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import UserCreateForm
from .permissions import require_capability, Capability


ALL_TOOLS = [
    {
        "name": "Zeszyt",
        "icon": "bi-journal-text",
        "url": "notebook",
        "status": "active",
        "areas": ["RC", "SP", "SA", "BD"],
    },
    {
        "name": "Grafik",
        "icon": "bi-calendar-week",
        "url": "schedule",
        "status": "planned",
        "areas": ["RC", "SA", "SP", "BD"],        
    },
    {
        "name": "Vouchery",
        "icon": "bi-card-list",
        "url": "voucher",
        "status": "planned",
        "areas": ["RC"],
    },
    {
        "name": "Stan gotówki",
        "icon": "bi-currency-exchange",
        "url": "balance",
        "status": "active",
        "areas": ["RC"],
    },
    {
        "name": "Formularze",
        "icon": "bi-ui-checks",
        "url": "forms",
        "status": "planned",
        "areas": ["RC", "SA", "BD"],
    },
    {
        "name": "Raporty",
        "icon": "bi-graph-up",
        "url": "reports",
        "status": "planned",
        "areas": ["RC", "SA", "SP", "BD"],
    },
    {
        "name": "Seanse saunowe",
        "icon": "bi-thermometer-half",
        "url": "saunas",
        "status": "active",
        "areas": ["RC", "SA", "BD"],
    },
    {
        "name": "Zajęcia",
        "icon": "bi-person-arms-up",
        "url": "classes",
        "status": "active",
        "areas": ["RC", "BD"],
    },
]

def root_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return redirect("login")


@login_required
@login_required
def dashboard_view(request):
    user = request.user
    area_code = user.area.code
    credentials = request.session.pop("new_user_credentials", None)

    visible_tools = []

    for tool in ALL_TOOLS:

        if tool["status"] == "planned" and not user.is_sys_admin:
            continue

        if "areas" in tool and area_code not in tool["areas"]:
            continue

        if "capability" in tool and not user.can(tool["capability"]):
            continue

        visible_tools.append(tool)

    return render(
        request,
        "accounts/dashboard.html",
        {
            "tools": visible_tools,
            "new_user_credentials": credentials,
        },
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



class ForcedPasswordChangeView(PasswordChangeView):
    template_name = "accounts/password_change.html"
    success_url = reverse_lazy("dashboard")

    def form_valid(self, form):
        response = super().form_valid(form)

        # reset flagi hasła
        self.request.user.must_change_password = False
        self.request.user.save(update_fields=["must_change_password"])

        return response
    

@require_capability(Capability.MANAGE_USERS)
def user_create_view(request):

    if request.method == "POST":
        form = UserCreateForm(request.POST)

        if form.is_valid():
            user, temp_password = form.save()

            request.session["new_user_credentials"] = {
                "email": user.email,
                "password": temp_password,
            }

            return redirect("dashboard")


    else:
        form = UserCreateForm()

    return render(
        request,
        "accounts/user_create.html",
        {
            "form": form,
        },
    )

