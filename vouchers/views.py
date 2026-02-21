from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Case, When, IntegerField
from .forms import VoucherCreateForm, VoucherEditForm, VoucherExtendForm, MPVTransactionForm
from .models import Voucher, MPVTransaction, VoucherLog
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.http import require_POST
from accounts.permissions import require_capability, Capability
from django.db import transaction
from django.core.paginator import Paginator
from django.utils.dateparse import parse_date



@login_required
@require_capability(Capability.CREATE_VOUCHERS)
def voucher_create_view(request):

    if request.method == "POST":
        form = VoucherCreateForm(request.POST)

        if form.is_valid():
            voucher = form.save(commit=False)
            voucher.seller = request.user
            voucher.save()
            
            VoucherLog.objects.create(
                voucher=voucher,
                action=VoucherLog.Action.CREATED,
                performed_by=request.user,
            )


            messages.success(request, "Vocher został dodany pomyślnie.")

            return redirect("vouchers:voucher_create")

    else:
        form = VoucherCreateForm()

    return render(request, "vouchers/create.html", {"form": form})



@login_required
@require_capability(Capability.VIEW_VOUCHERS)
def voucher_search_view(request):

    query = request.GET.get("q", "").strip()
    page_number = request.GET.get("page")

    results = Voucher.objects.none()

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

    paginator = Paginator(results, 10)  # 10 wyników na stronę
    page_obj = paginator.get_page(page_number)

    context = {
        "query": query,
        "results": page_obj,
        "page_obj": page_obj,
    }

    return render(request, "vouchers/search.html", context)



@login_required
@require_POST
@require_capability(Capability.REDEEM_VOUCHERS)
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

    VoucherLog.objects.create(
        voucher=voucher,
        action=VoucherLog.Action.STATUS_CHANGED,
        performed_by=request.user,
        description="Voucher oznaczony jako zużyty"
    )


    messages.success(request, "Voucher został oznaczony jako zużyty.")

    next_url = request.POST.get("next") or request.GET.get("next")
    return redirect(next_url or "vouchers:voucher_search")


@login_required
@require_capability(Capability.EDIT_VOUCHERS)
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

            VoucherLog.objects.create(
                voucher=voucher,
                action=VoucherLog.Action.EDITED,
                performed_by=request.user,
                description="Zmieniono client_name"
            )


            messages.success(request, "Voucher został zaktualizowany.")
            next_url = request.POST.get("next") or request.GET.get("next")
            return redirect(next_url or "vouchers:voucher_search")

    return render(
        request,
        "vouchers/edit.html",
        {
            "form": form,
            "voucher": voucher,
        }
    )



@login_required
@require_capability(Capability.EXTEND_VOUCHERS)
def voucher_extend_view(request, pk):
    voucher = get_object_or_404(Voucher, pk=pk)

    if voucher.effective_status not in [
        Voucher.Status.ACTIVE,
        Voucher.Status.EXPIRED,
    ]:

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

            VoucherLog.objects.create(
                voucher=voucher,
                action=VoucherLog.Action.EXTENDED,
                performed_by=request.user,
                description="Zmieniono expiry_date"
            )


            messages.success(request, "Voucher został przedłużony.")
            next_url = request.POST.get("next") or request.GET.get("next")
            return redirect(next_url or "vouchers:voucher_search")

    else:
        form = VoucherExtendForm(instance=voucher)

    return render(request, "vouchers/extend.html", {
        "form": form,
        "voucher": voucher,
    })


@login_required
@require_capability(Capability.MPV_TRANSACTIONS)
def voucher_transaction_view(request, pk):
    voucher = get_object_or_404(Voucher, pk=pk)

    if voucher.type != Voucher.Type.MPV:
        messages.error(request, "Transakcje dostępne tylko dla MPV.")
        return redirect("vouchers:voucher_search")

    if voucher.effective_status != Voucher.Status.ACTIVE:
        messages.error(request, "Transakcja możliwa tylko dla aktywnego MPV.")
        return redirect("vouchers:voucher_search")

    # ====== CONFIRM CARD RETURN ======
    if request.method == "POST" and "confirm_return" in request.POST:

        with transaction.atomic():
            voucher = Voucher.objects.select_for_update().get(pk=voucher.pk)

            if request.POST.get("confirm_return") == "yes":
                voucher.status = Voucher.Status.ZERO_RETURNED
            else:
                voucher.status = Voucher.Status.ZERO_NOT_RETURNED

            voucher.save(update_fields=["status", "updated_at"])

        messages.success(request, "Status karty zaktualizowany.")
        next_url = request.POST.get("next") or request.GET.get("next")
        return redirect(next_url or "vouchers:voucher_search")

    # ====== NORMAL TRANSACTION ======
    if request.method == "POST":
        form = MPVTransactionForm(request.POST)

        if form.is_valid():

            with transaction.atomic():

                voucher = Voucher.objects.select_for_update().get(pk=voucher.pk)

                transaction_obj = MPVTransaction.objects.create(
                    voucher=voucher,
                    amount=form.cleaned_data["amount"],
                    note=form.cleaned_data.get("note", ""),
                    created_by=request.user,
                )

                # saldo aktualizuje model save()
                voucher.refresh_from_db()

                VoucherLog.objects.create(
                    voucher=voucher,
                    action=VoucherLog.Action.TRANSACTION,
                    performed_by=request.user,
                    description=f"Kwota: {transaction_obj.amount}"
                )

            if voucher.value_remaining == 0:
                return redirect(f"{request.path}?confirm_return=1")

            messages.success(request, "Transakcja zapisana.")
            next_url = request.POST.get("next") or request.GET.get("next")
            return redirect(next_url or "vouchers:voucher_search")

    else:
        form = MPVTransactionForm()

    show_modal = request.GET.get("confirm_return") == "1"

    return render(request, "vouchers/transaction.html", {
        "form": form,
        "voucher": voucher,
        "show_modal": show_modal,
    })



@login_required
@require_capability(Capability.VIEW_VOUCHER_LOGS)
def voucher_logs_view(request):

    if not request.user.is_superuser:
        return redirect("dashboard")

    logs = (
        VoucherLog.objects
        .select_related("voucher", "performed_by")
        .order_by("-created_at")
    )

    paginator = Paginator(logs, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "vouchers/logs.html", {
        "logs": logs,
        "page_obj": page_obj,
    })

@login_required
@require_capability(Capability.VIEW_VOUCHERS)
def voucher_list_view(request):

    vouchers = Voucher.objects.all().select_related("seller")

    # --- FILTR TYP ---
    voucher_type = request.GET.get("type")
    if voucher_type and voucher_type != "ALL":
        vouchers = vouchers.filter(voucher_type=voucher_type)

    # --- FILTR DAT ---
    date_from = request.GET.get("from")
    date_to = request.GET.get("to")

    if date_from:
        vouchers = vouchers.filter(created_at__date__gte=parse_date(date_from))

    if date_to:
        vouchers = vouchers.filter(created_at__date__lte=parse_date(date_to))

    # --- SORTOWANIE ---
    order = request.GET.get("order", "asc")

    if order == "desc":
        vouchers = vouchers.order_by("-created_at")
    else:
        vouchers = vouchers.order_by("created_at")

    # --- PAGINACJA ---
    paginator = Paginator(vouchers, 50)  # 50 na stronę
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "voucher_type": voucher_type,
        "date_from": date_from,
        "date_to": date_to,
        "order": order,
    }

    return render(request, "vouchers/voucher_list.html", context)