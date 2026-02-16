from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from .models import Voucher
from decimal import Decimal


class VoucherCreateForm(forms.ModelForm):

    # ZAMIANA ModelChoiceField → CharField
    mpv_card_code = forms.CharField(
        required=False,
        label="Kod karty MPV",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = Voucher
        fields = [
            "type",
            "code",
            "mpv_card_code",
            "client_name",
            "service_name",
            "receipt_number",
            "expiry_date",
            "value_total",
            "notes",
        ]
        widgets = {
            "code": forms.TextInput(attrs={"class": "form-control"}),
            "client_name": forms.TextInput(attrs={"class": "form-control"}),
            "service_name": forms.TextInput(attrs={"class": "form-control"}),
            "receipt_number": forms.TextInput(attrs={"class": "form-control"}),
            "value_total": forms.NumberInput(attrs={"class": "form-control"}),
            "expiry_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "type": forms.Select(attrs={"class": "form-select"}),
            "notes": forms.TextInput(attrs={"class": "form-control", "rows": 4}),
        }

    def clean(self):

        today = timezone.localdate()

    # =============================
    # MPV
    # =============================

        if self.type == self.Type.MPV:

            if not self.mpv_card:
                raise ValidationError("MPV musi mieć przypisaną kartę.")

            if self.value_total is None:
                raise ValidationError("MPV musi mieć wartość początkową.")

            if self.value_total < Decimal("0.00"):
                raise ValidationError("Wartość MPV nie może być ujemna.")

            # ustawienie początkowego salda
            if self.pk is None:
                self.value_remaining = self.value_total

            existing_active = Voucher.objects.filter(
                mpv_card=self.mpv_card,
                type=self.Type.MPV,
                status__in=[
                    self.Status.ACTIVE,
                    self.Status.ZERO_NOT_RETURNED
                ]
            ).exclude(pk=self.pk)

            if existing_active.exists():
                raise ValidationError("Ta karta ma już aktywny voucher.")

    # =============================
    # SPV / OLD
    # =============================

        else:

            if not self.code:
                raise ValidationError("Voucher musi mieć kod.")

            if self.mpv_card:
                raise ValidationError("Tylko MPV może mieć kartę.")

    # =============================
    # SPV specific
    # =============================

        if self.type == self.Type.SPV:

            if not self.service_name:
                raise ValidationError("SPV musi mieć nazwę usługi.")

            if self.value_remaining:
                raise ValidationError("SPV nie może mieć value_remaining.")

    # =============================
    # Expiry defaults
    # =============================

        if not self.expiry_date:

            if self.type == self.Type.MPV:
                self.expiry_date = today + timedelta(days=180)

            elif self.type == self.Type.SPV:
                self.expiry_date = today + timedelta(days=90)

    # =============================
    # Auto expired
    # =============================

        if self.is_expired and self.status == self.Status.ACTIVE:
            self.status = self.Status.EXPIRED
   

    def save(self, commit=True):
        instance = super().save(commit=False)

        voucher_type = self.cleaned_data.get("type")

        if voucher_type == Voucher.Type.MPV:
            instance.mpv_card = self.cleaned_data["mpv_card"]
            instance.value_remaining = self.cleaned_data["value_remaining"]

        if commit:
            instance.full_clean()
            instance.save()

        return instance

  