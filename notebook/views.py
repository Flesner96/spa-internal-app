from django.shortcuts import render, redirect, get_object_or_404
from .forms import AreaMessageForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import AreaMessage
from django.utils import timezone
from django.http import HttpResponseForbidden, FileResponse, Http404
from core.rbac.permissions import Capability
from core.rbac.decorators import require_capability
from .forms import AreaMessageReplyForm


@login_required
def edit_area_message(request, pk):
    message = get_object_or_404(AreaMessage, pk=pk)

    if hasattr(message, "reply"):
        return HttpResponseForbidden(
            "Nie można edytować wiadomości z odpowiedzią."
        )
    if not request.user.can(Capability.EDIT_NOTEBOOK):
        return HttpResponseForbidden()

    if message.author != request.user:
        return HttpResponseForbidden()

    if request.method == "POST":
        form = AreaMessageForm(request.POST, request.FILES, instance=message)
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
@require_capability(Capability.VIEW_NOTEBOOK)
def notebook_view(request):
    area = request.user.area

    messages_qs = (
        AreaMessage.objects
        .filter(area=area)
        .order_by("-created_at")
    )

    paginator = Paginator(messages_qs, 5)  # ⬅️ ile wpisów na stronę
    page_number = request.GET.get("page")
    area_messages = paginator.get_page(page_number)
    reply_form = AreaMessageReplyForm()

    if request.method == "POST":
        if not request.user.can(Capability.POST_NOTEBOOK):
            return HttpResponseForbidden()
        
        form = AreaMessageForm(request.POST, request.FILES)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.author = request.user
            msg.area = area
            msg.save()
            return redirect("notebook")


    else:
        form = AreaMessageForm()

    return render(
        request,
        "notebook/notebook.html",
        {
            "area_messages": area_messages,
            "form": form,
            "reply_form": reply_form,
        }
    )

@login_required
@require_capability(Capability.VIEW_NOTEBOOK)
def download_area_message_attachment(request, pk):
    
    msg = get_object_or_404(AreaMessage, pk=pk)

    if msg.area != request.user.area:
        raise Http404()

    if not msg.attachment:
        raise Http404()

    return FileResponse(
        msg.attachment.open("rb"),
        as_attachment=True,
        filename=msg.attachment.name.split("/")[-1],
    )





@login_required
@require_capability(Capability.REPLY_NOTEBOOK)
def reply_area_message(request, pk):
    message = get_object_or_404(AreaMessage, pk=pk)

    if hasattr(message, "reply"):
        return HttpResponseForbidden("Ta wiadomość ma już odpowiedź.")

    if request.method == "POST":
        form = AreaMessageReplyForm(request.POST)

        if form.is_valid():
            reply = form.save(commit=False)
            reply.message = message
            reply.author = request.user
            reply.save()

    return redirect("notebook")
