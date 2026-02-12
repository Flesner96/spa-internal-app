from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import CashCountForm
from .models import CashCount
from .utils import calculate_total


@login_required
def balance_view(request):
    if request.method == "POST":
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

            messages.success(
                request,
                f"Stan kasy zapisany: {total} zł"
            )

            return redirect("balance")

    else:
        form = CashCountForm()

    return render(
        request,
        "balance/calculator.html",
        {"form": form},
    )
