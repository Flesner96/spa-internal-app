from django.shortcuts import render, redirect, get_object_or_404
from .forms import AreaMessageForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import AreaMessage
from django.utils import timezone
from django.http import HttpResponseForbidden, FileResponse, Http404
from django.urls import reverse

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
            return redirect("notebook")
    else:
        form = AreaMessageForm(instance=message)

    return render(
        request,
        "notebook/edit_message.html",
        {"form": form, "message": message},
    )

@login_required
def notebook_view(request):
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

        form = AreaMessageForm(request.POST, request.FILES)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.author = request.user
            msg.area = area
            msg.save()
            return redirect(f"{reverse('notebook')}?page={messages.number}")

    else:
        form = AreaMessageForm()

    return render(
        request,
        "notebook/notebook.html",
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