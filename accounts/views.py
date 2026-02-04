from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import AreaMessage
from .forms import AreaMessageForm, UserProfileForm


def root_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return redirect("login")


@login_required
def dashboard_view(request):
    user = request.user
    area = user.area
    messages = AreaMessage.objects.filter(area=area)

    if request.method == "POST":
        form = AreaMessageForm(request.POST, request.FILES)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.author = user
            msg.area = area
            msg.save()
            return redirect("dashboard")
    else:
        form = AreaMessageForm()

    context = {
        "messages": messages[:5],  
        "form": form,
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