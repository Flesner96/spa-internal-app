from django.db import models
from django.conf import settings
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta


class MPVCard(models.Model):
    code = models.CharField(max_length=10, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["code"]),
        ]

    def __str__(self):
        return self.code


class Voucher(models.Model):

    class Type(models.TextChoices):
        MPV = "MPV", "MPV"
        SPV = "SPV", "SPV"
        OLD = "OLD", "STARY"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        USED = "used", "Used"
        ZERO_NOT_RETURNED = "zero_not_returned", "Zero – not returned"
        ZERO_RETURNED = "zero_returned", "Zero – returned"
        EXPIRED = "expired", "Expired"

    type = models.CharField(max_length=3, choices=Type.choices)

    # SPV / OLD
    code = models.CharField(max_length=20, blank=True)

    # MPV
    mpv_card = models.ForeignKey(
        MPVCard,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="vouchers",
    )

    client_name = models.CharField(max_length=150)
    receipt_number = models.CharField(max_length=50, blank=True)

    issue_date = models.DateTimeField(auto_now_add=True)

    expiry_date = models.DateField(blank=True, null=True)
    extended_until = models.DateField(null=True, blank=True)
    extended_reason = models.CharField(max_length=255, blank=True)

    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="sold_vouchers"
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    # MPV
    value_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    value_remaining = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    # SPV
    service_name = models.CharField(max_length=200, blank=True)
    redeemed_at = models.DateTimeField(null=True, blank=True)

    notes = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["client_name"]),
            models.Index(fields=["status"]),
            models.Index(fields=["voucher_type"]),
            models.Index(fields=["issue_date"]),
        ]

    # ======================================
    # PROPERTY: is_expired
    # ======================================

    @property
    def is_expired(self):
        if not self.expiry_date and not self.extended_until:
            return False

        today = timezone.localdate()
        effective_expiry = self.extended_until or self.expiry_date
        return effective_expiry < today
    
    # ======================================
    # PROPERTY: effective_status
    # ======================================

    @property
    def effective_status(self):
        if self.status == self.Status.ACTIVE and self.is_expired:
            return self.Status.EXPIRED
        return self.status
    
    # ======================================
    # PROPERTY: display
    # ======================================

    @property
    def display_status(self):
        mapping = {
            "active": "AKTYWNY",
            "used": "ZUŻYTY",
            "expired": "WYGASŁ",
            "zero_not_returned": "WYKORZYSTANY – KARTA NIEODDANA",
            "zero_returned": "WYKORZYSTANY – KARTA ZWRÓCONA",
        }
        return mapping.get(self.effective_status, self.effective_status)

    @property
    def display_type(self):
        mapping = {
            "MPV": "MPV",
            "SPV": "SPV",
            "OLD": "STARY",
        }
        return mapping.get(self.type, self.type)
    
    @property
    def display_seller(self):
        if not self.seller:
            return "-"
        return self.seller.first_name or self.seller.email


    # ======================================
    # CLEAN LOGIC
    # ======================================

    def clean(self):

        today = timezone.localdate()

        # -----------------------------
        # TYPE VALIDATION
        # -----------------------------

        if self.type == self.Type.MPV:

            if self.value_total is None:
                raise ValidationError("MPV musi mieć wartość początkową.")

            if self.value_total < Decimal("0.00"):
                raise ValidationError("Wartość MPV nie może być ujemna.")

            # ustawienie początkowego salda przy tworzeniu
            if self.pk is None:
                self.value_remaining = self.value_total

            # blokada aktywnej karty
            existing_active = Voucher.objects.filter(
                mpv_card=self.mpv_card,
                type=self.Type.MPV,
                status__in=[
                    self.Status.ACTIVE,
                    self.Status.ZERO_NOT_RETURNED
                ]
            ).exclude(pk=self.pk)

            if existing_active.exists():
                raise ValidationError(
                    "Ta karta ma już aktywny voucher."
                )

        else:
            # SPV / OLD muszą mieć kod
            if not self.code:
                raise ValidationError("Voucher musi mieć kod.")

            if self.type == self.Type.MPV and self.mpv_card is None:
                raise ValidationError("MPV musi mieć przypisaną kartę.")


        # -----------------------------
        # SPV SPECIFIC
        # -----------------------------

        if self.type == self.Type.SPV:

            if not self.service_name:
                raise ValidationError("SPV musi mieć nazwę usługi.")

            if self.value_remaining:
                raise ValidationError("SPV nie może mieć value_remaining.")

        # -----------------------------
        # EXPIRY DEFAULT
        # -----------------------------

        if not self.expiry_date:

            if self.type == self.Type.MPV:
                self.expiry_date = today + timedelta(days=180)

            elif self.type == self.Type.SPV:
                self.expiry_date = today + timedelta(days=90)

        # -----------------------------
        # AUTO STATUS EXPIRED
        # -----------------------------

        if self.is_expired and self.status == self.Status.ACTIVE:
            self.status = self.Status.EXPIRED

    def __str__(self):
        if self.type == self.Type.MPV:
            return f"MPV {self.mpv_card.code} – {self.client_name}"
        return f"{self.type} {self.code} – {self.client_name}"



class MPVTransaction(models.Model):

    voucher = models.ForeignKey(
        Voucher,
        on_delete=models.CASCADE,
        related_name="transactions"
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    created_at = models.DateTimeField(auto_now_add=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    note = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def clean(self):

        # 🔐 zabezpieczenie — jeśli voucher nie jest ustawiony
        if not self.voucher_id:
            raise ValidationError("Voucher nie został przypisany.")

        if self.voucher.type != Voucher.Type.MPV:
            raise ValidationError("Transakcje tylko dla MPV.")

        if self.amount is None or self.amount <= Decimal("0.00"):
            raise ValidationError("Kwota musi być dodatnia.")

        if self.voucher.value_remaining is None:
            raise ValidationError("Voucher nie ma salda.")

        if self.amount > self.voucher.value_remaining:
            raise ValidationError("Brak wystarczających środków.")

    def save(self, *args, **kwargs):

        is_new = self.pk is None

        super().save(*args, **kwargs)

        if is_new:
            voucher = self.voucher
            voucher.value_remaining -= self.amount

            if voucher.value_remaining <= Decimal("0.00"):
                voucher.value_remaining = Decimal("0.00")

            voucher.save(update_fields=["value_remaining", "updated_at"])

    def __str__(self):
        return f"{self.voucher} – {self.amount}"


class VoucherLog(models.Model):

    class Action(models.TextChoices):
        CREATED = "created", "Created"
        EDITED = "edited", "Edited"
        EXTENDED = "extended", "Extended"
        STATUS_CHANGED = "status_changed", "Status changed"
        TRANSACTION = "transaction", "MPV transaction"

    voucher = models.ForeignKey(
        Voucher,
        on_delete=models.CASCADE,
        related_name="logs"
    )

    action = models.CharField(max_length=30, choices=Action.choices)

    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.voucher} – {self.action}"
