from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .models import Voucher, MPVCard, MPVTransaction


class VoucherCreateForm(forms.ModelForm):

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
            "type": forms.Select(attrs={"class": "form-control"}),
            "code": forms.TextInput(attrs={"class": "form-control"}),
            "client_name": forms.TextInput(attrs={"class": "form-control"}),
            "service_name": forms.TextInput(attrs={"class": "form-control"}),
            "receipt_number": forms.TextInput(attrs={"class": "form-control"}),
            "expiry_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "value_total": forms.NumberInput(attrs={"class": "form-control"}),
            "notes": forms.Textarea(attrs={"class": "form-control"}),
        }

    def clean(self):
        cleaned_data = super().clean()

        voucher_type = cleaned_data.get("type")
        mpv_card_code = cleaned_data.get("mpv_card_code")
        code = cleaned_data.get("code")
        value_total = cleaned_data.get("value_total")
        expiry_date = cleaned_data.get("expiry_date")

        today = timezone.localdate()

        # =============================
        # MPV
        # =============================

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

            if value_total <= Decimal("0.00"):
                raise ValidationError("Wartość MPV musi być większa niż 0.")

            cleaned_data["value_remaining"] = value_total

            cleaned_data["expiry_date"] = today + timedelta(days=180)

        # =============================
        # SPV
        # =============================

        elif voucher_type == Voucher.Type.SPV:

            if not code:
                raise ValidationError("SPV musi mieć kod.")

            if not cleaned_data.get("service_name"):
                raise ValidationError("SPV musi mieć nazwę usługi.")

            cleaned_data["expiry_date"] = today + timedelta(days=90)

        # =============================
        # OLD
        # =============================

        elif voucher_type == Voucher.Type.OLD:

            if not code:
                raise ValidationError("OLD musi mieć kod.")

            if not expiry_date:
                raise ValidationError("Dla OLD musisz ręcznie ustawić datę ważności.")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        voucher_type = self.cleaned_data.get("type")

        if voucher_type == Voucher.Type.MPV:
            instance.mpv_card = self.cleaned_data["mpv_card"]
            instance.value_remaining = self.cleaned_data["value_remaining"]

        if commit:
            instance.save()

        return instance


class VoucherEditForm(forms.ModelForm):

    class Meta:
        model = Voucher
        fields = [
            "client_name",
            "service_name",
            "receipt_number",
            "expiry_date",
            "notes",
        ]
        widgets = {
            "expiry_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "notes": forms.Textarea(attrs={"class": "form-control"}),
            "client_name": forms.TextInput(attrs={"class": "form-control"}),
            "service_name": forms.TextInput(attrs={"class": "form-control"}),
            "receipt_number": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        voucher = self.instance

        # blokada gdy zużyty
        if voucher.effective_status in [
            Voucher.Status.USED,
            Voucher.Status.ZERO_NOT_RETURNED,
            Voucher.Status.ZERO_RETURNED,
        ]:
            for field in self.fields.values():
                field.disabled = True

        # expiry tylko dla OLD
        if voucher.type != Voucher.Type.OLD:
            self.fields["expiry_date"].widget = forms.HiddenInput()

        # service tylko dla SPV / OLD
        if voucher.type == Voucher.Type.MPV:
            self.fields["service_name"].widget = forms.HiddenInput()


class VoucherExtendForm(forms.ModelForm):
    class Meta:
        model = Voucher
        fields = ["extended_until", "extended_reason"]

        widgets = {
            "extended_until": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "extended_reason": forms.TextInput(
                attrs={"class": "form-control"}
            ),
        }

    def clean(self):
        cleaned = super().clean()

        new_date = cleaned.get("extended_until")

        if not new_date:
            raise forms.ValidationError("Musisz podać nową datę ważności.")

        if new_date <= self.instance.expiry_date:
            raise forms.ValidationError(
                "Nowa data musi być późniejsza niż aktualna."
            )

        return cleaned
    

class MPVTransactionForm(forms.ModelForm):

    card_returned = forms.BooleanField(
        required=False,
        label="Karta oddana do recepcji?"
    )

    class Meta:
        model = MPVTransaction
        fields = ["amount", "note"]
        widgets = {
            "amount": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "note": forms.TextInput(
                attrs={"class": "form-control"}
            ),
        }

    def __init__(self, *args, **kwargs):
        self.voucher = kwargs.pop("voucher")
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        amount = cleaned.get("amount")

        if amount is None:
            raise forms.ValidationError("Podaj kwotę.")

        if amount <= Decimal("0.00"):
            raise forms.ValidationError("Kwota musi być większa niż 0.")

        if amount > self.voucher.value_remaining:
            raise forms.ValidationError("Kwota przekracza dostępne saldo.")

        return cleaned

