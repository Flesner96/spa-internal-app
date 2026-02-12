from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import CashCountForm
from .models import CashCount
from .utils import calculate_total


@login_required
def balance_view(request):
    last_count = (
        CashCount.objects
        .filter(area=request.user.area)
        .first()
    )

    saved_total = None

    if request.method == "POST":
        form = CashCountForm(request.POST)

        if form.is_valid():
            breakdown = form.cleaned_data
            total = calculate_total(breakdown)

            count = CashCount.objects.create(
                user=request.user,
                area=request.user.area,
                breakdown=breakdown,
                total=total,
            )

            saved_total = total
            last_count = count
            form = CashCountForm()  # reset form

    else:
        form = CashCountForm()

    return render(
        request,
        "balance/calculator.html",
        {
            "form": form,
            "saved_total": saved_total,
            "last_count": last_count,
        },
    )
