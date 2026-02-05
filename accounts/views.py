from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden, FileResponse, Http404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import AreaMessage
from .forms import AreaMessageForm, UserProfileForm
from django.core.paginator import Paginator

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
                "url": "board",
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
                "url": "board",
                "enabled": True,
            },
            
        ],
        "SA": [
            {
                "name": "Zeszyt",
                "icon": "bi-journal-text",
                "url": "board",
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
                "url": "board",
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


@login_required
def edit_area_message(request, pk):
    message = get_object_or_404(AreaMessage, pk=pk)

    # TYLKO autor może edytować
    if message.author != request.user:
        return HttpResponseForbidden("Nie masz uprawnień do edycji tego wpisu.")

    if request.method == "POST":
        form = AreaMessageForm(request.POST, instance=message)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.is_edited = True
            msg.edited_at = timezone.now()
            msg.save()
            return redirect("dashboard")
    else:
        form = AreaMessageForm(instance=message)

    return render(
        request,
        "accounts/edit_message.html",
        {"form": form, "message": message},
    )

@login_required
def board_view(request):
    area = request.user.area

    messages_qs = (
        AreaMessage.objects
        .filter(area=area)
        .order_by("-created_at")
    )

    paginator = Paginator(messages_qs, 5)  # ⬅️ ile wpisów na stronę
    page_number = request.GET.get("page")
    messages = paginator.get_page(page_number)

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect("login")

        form = AreaMessageForm(request.POST, request.FILES)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.author = request.user
            msg.area = area
            msg.save()
            return redirect("board")
    else:
        form = AreaMessageForm()

    return render(
        request,
        "accounts/board.html",
        {
            "messages": messages,
            "form": form,
        }
    )

@login_required
def download_area_message_attachment(request, pk):
    msg = get_object_or_404(AreaMessage, pk=pk)

    # 🔒 bezpieczeństwo: tylko ta sama area
    if msg.area != request.user.area:
        raise Http404()

    if not msg.attachment:
        raise Http404()

    return FileResponse(
        msg.attachment.open("rb"),
        as_attachment=True,
        filename=msg.attachment.name.split("/")[-1],
    )