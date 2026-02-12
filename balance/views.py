from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from accounts.permissions import Capability
from .forms import CashCountForm
from .models import CashCount
from .utils import calculate_total
from django.core.paginator import Paginator

@login_required
def balance_view(request):

    if not request.user.can(Capability.VIEW_BALANCE):
        return HttpResponseForbidden()

    # 👉 odbieramy saved_total z poprzedniego POST (jeśli był)
    saved_total = request.session.pop("saved_total", None)

    if request.method == "POST":

        if not request.user.can(Capability.CREATE_BALANCE):
            return HttpResponseForbidden()

        form = CashCountForm(request.POST)

        if form.is_valid():

            breakdown = form.cleaned_data
            total = calculate_total(breakdown)

            CashCount.objects.create(
                user=request.user,
                area=request.user.area,
                breakdown=breakdown,
                total=total,
            )

            # 👉 zapisujemy do session
            request.session["saved_total"] = str(total)

            # 👉 redirect after POST
            return redirect("balance")

    else:
        form = CashCountForm()

    # 👉 zawsze pobieramy ostatni stan po redirect
    last_count = (
        CashCount.objects
        .filter(area=request.user.area)
        .order_by("-created_at")
        .first()
    )

    return render(
        request,
        "balance/calculator.html",
        {
            "form": form,
            "saved_total": saved_total,
            "last_count": last_count,
        },
    )

@login_required
def balance_history_view(request):

    if not request.user.can(Capability.BALANCE_HISTORY):
        return HttpResponseForbidden()

    counts = CashCount.objects.select_related("user").order_by("-created_at")

    paginator = Paginator(counts, 25)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "balance/history.html",
        {
            "page_obj": page_obj,
        },
    )
