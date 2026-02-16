from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from .models import Voucher, MPVCard


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
        cleaned_data = super().clean()

        voucher_type = cleaned_data.get("type")
        mpv_card_code = cleaned_data.get("mpv_card_code")
        code = cleaned_data.get("code")
        value_total = cleaned_data.get("value_total")
        expiry_date = cleaned_data.get("expiry_date")

        # -------------------------
        # MPV
        # -------------------------

        if voucher_type == Voucher.Type.MPV:

            if not mpv_card_code:
                raise ValidationError("MPV musi mieć kod karty.")

            try:
                card = MPVCard.objects.get(code=mpv_card_code)
            except MPVCard.DoesNotExist:
                raise ValidationError("Karta MPV o takim kodzie nie istnieje.")

            existing = Voucher.objects.filter(
                mpv_card=card,
                status__in=[
                    Voucher.Status.ACTIVE,
                    Voucher.Status.ZERO_NOT_RETURNED
                ]
            )           

            if existing.exists():
                raise ValidationError("Ta karta ma już aktywny voucher.")


            cleaned_data["mpv_card"] = card

            if value_total is None:
                raise ValidationError("MPV musi mieć wartość.")

            cleaned_data["value_remaining"] = value_total

            if not expiry_date:
                cleaned_data["expiry_date"] = (
                    timezone.localdate() + timedelta(days=180)
                )

        # -------------------------
        # SPV
        # -------------------------

        elif voucher_type == Voucher.Type.SPV:

            if not code:
                raise ValidationError("SPV musi mieć kod.")

            if not expiry_date:
                cleaned_data["expiry_date"] = (
                    timezone.localdate() + timedelta(days=90)
                )

        # -------------------------
        # OLD
        # -------------------------

        elif voucher_type == Voucher.Type.OLD:

            if not code:
                raise ValidationError("OLD musi mieć kod.")

            if not expiry_date:
                raise ValidationError(
                    "Dla OLD musisz ręcznie ustawić datę ważności."
                )
            
        if not cleaned_data.get("expiry_date"):
            raise ValidationError("Data ważności nie została ustawiona.")


        return cleaned_data

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

  