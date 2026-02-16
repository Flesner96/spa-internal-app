from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Case, When, IntegerField
from .forms import VoucherCreateForm, VoucherEditForm, VoucherExtendForm, MPVTransactionForm
from .models import Voucher, MPVTransaction
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.http import require_POST





@login_required
def voucher_create_view(request):

    if request.method == "POST":
        form = VoucherCreateForm(request.POST)

        if form.is_valid():
            voucher = form.save(commit=False)
            voucher.seller = request.user
            voucher.save()
            
            messages.success(request, "Vocher został dodany pomyślnie.")

            return redirect("vouchers:voucher_create")

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


@login_required
@require_POST
def voucher_redeem_view(request, pk):
    voucher = get_object_or_404(Voucher, pk=pk)

    # tylko SPV / OLD
    if voucher.type == Voucher.Type.MPV:
        messages.error(request, "MPV nie można oznaczyć jako zużyty.")
        return redirect("vouchers:voucher_search")

    # tylko active
    if voucher.effective_status != Voucher.Status.ACTIVE:
        messages.error(request, "Voucher nie jest aktywny.")
        return redirect("vouchers:voucher_search")

    voucher.status = Voucher.Status.USED
    voucher.redeemed_at = timezone.now()
    voucher.save(update_fields=["status", "redeemed_at", "updated_at"])

    messages.success(request, "Voucher został oznaczony jako zużyty.")

    return redirect("vouchers:voucher_search")


@login_required
def voucher_edit_view(request, pk):
    voucher = get_object_or_404(Voucher, pk=pk)

    form = VoucherEditForm(
        request.POST or None,
        instance=voucher
    )

    if request.method == "POST":
        if voucher.effective_status in [
            Voucher.Status.USED,
            Voucher.Status.ZERO_NOT_RETURNED,
            Voucher.Status.ZERO_RETURNED,
        ]:
            messages.error(request, "Tego vouchera nie można edytować.")
            return redirect("vouchers:voucher_search")

        if form.is_valid():
            form.save()
            messages.success(request, "Voucher został zaktualizowany.")
            return redirect("vouchers:voucher_search")

    return render(
        request,
        "vouchers/edit.html",
        {
            "form": form,
            "voucher": voucher,
        }
    )



@login_required
def voucher_extend_view(request, pk):
    voucher = get_object_or_404(Voucher, pk=pk)

    if voucher.effective_status not in ["active", "expired"]:
        messages.error(request, "Nie można przedłużyć tego vouchera.")
        return redirect("vouchers:voucher_search")

    if request.method == "POST":
        form = VoucherExtendForm(request.POST, instance=voucher)

        if form.is_valid():
            voucher = form.save(commit=False)

            # jeżeli był expired — wraca do active
            if voucher.status == Voucher.Status.EXPIRED:
                voucher.status = Voucher.Status.ACTIVE

            voucher.save()

            messages.success(request, "Voucher został przedłużony.")
            return redirect("vouchers:voucher_search")

    else:
        form = VoucherExtendForm(instance=voucher)

    return render(request, "vouchers/extend.html", {
        "form": form,
        "voucher": voucher,
    })


@login_required
def voucher_transaction_view(request, pk):
    voucher = get_object_or_404(Voucher, pk=pk)

    if voucher.type != Voucher.Type.MPV:
        messages.error(request, "Transakcje dostępne tylko dla MPV.")
        return redirect("vouchers:voucher_search")

    if voucher.effective_status != "active":
        messages.error(request, "Transakcja możliwa tylko dla aktywnego MPV.")
        return redirect("vouchers:voucher_search")

    if request.method == "POST":
        form = MPVTransactionForm(request.POST, voucher=voucher)
        print(voucher)
        if form.is_valid():
            transaction = MPVTransaction(
                voucher=voucher,  # ← przypisujemy NAJPIERW
                amount=form.cleaned_data["amount"],
                note=form.cleaned_data.get("note", ""),
                created_by=request.user,
            )

            transaction.save()  # model zrobi full_clean + logikę salda

            messages.success(request, "Transakcja zapisana.")
            return redirect("vouchers:voucher_search")

    else:
        form = MPVTransactionForm(voucher=voucher)

    return render(request, "vouchers/transaction.html", {
        "form": form,
        "voucher": voucher,
    })
