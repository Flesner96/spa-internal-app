from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Case, When, IntegerField
from .forms import VoucherCreateForm
from .models import Voucher



@login_required
def voucher_create_view(request):

    if request.method == "POST":
        form = VoucherCreateForm(request.POST)

        if form.is_valid():
            voucher = form.save(commit=False)
            voucher.seller = request.user
            voucher.save()

            return redirect("voucher_create")

    else:
        form = VoucherCreateForm()

    return render(request, "vouchers/create.html", {"form": form})



@login_required
def voucher_search_view(request):

    query = request.GET.get("q", "").strip()
    results = []

    if query:

        results = (
            Voucher.objects
            .select_related("mpv_card", "seller")
            .filter(
                Q(code__icontains=query) |
                Q(mpv_card__code__icontains=query) |
                Q(client_name__icontains=query)
            )
            .annotate(
                status_order=Case(
                    When(status=Voucher.Status.ACTIVE, then=0),
                    When(status=Voucher.Status.EXPIRED, then=1),
                    default=2,
                    output_field=IntegerField(),
                )
            )
            .order_by("status_order", "-issue_date")
        )

    context = {
        "query": query,
        "results": results,
    }

    return render(request, "vouchers/search.html", context)
