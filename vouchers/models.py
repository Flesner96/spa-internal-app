from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal


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
        OLD = "OLD", "OLD"

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
    expiry_date = models.DateField()
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
    service_name = models.CharField(
        max_length=200,
        blank=True,
    )

    redeemed_at = models.DateTimeField(null=True, blank=True)

    notes = models.TextField(blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["client_name"]),
            models.Index(fields=["status"]),
        ]

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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Aktualizacja salda
        voucher = self.voucher
        voucher.value_remaining = (
            voucher.value_remaining - self.amount
        )

        if voucher.value_remaining <= Decimal("0.00"):
            voucher.value_remaining = Decimal("0.00")
            voucher.status = Voucher.Status.ZERO_NOT_RETURNED

        voucher.save()

    def __str__(self):
        return f"{self.voucher} – {self.amount}"
