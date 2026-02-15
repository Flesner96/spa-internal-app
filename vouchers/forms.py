from django import forms
from django.utils import timezone
from .models import Voucher, MPVCard


class VoucherCreateForm(forms.ModelForm):

    class Meta:
        model = Voucher
        fields = [
            "type",
            "code",
            "mpv_card",
            "client_name",
            "receipt_number",
            "service_name",
            "value_total",
            "notes",
        ]

        widgets = {
            "type": forms.Select(attrs={"class": "form-select"}),
            "code": forms.TextInput(attrs={"class": "form-control"}),
            "mpv_card": forms.Select(attrs={"class": "form-select"}),
            "client_name": forms.TextInput(attrs={"class": "form-control"}),
            "receipt_number": forms.TextInput(attrs={"class": "form-control"}),
            "service_name": forms.TextInput(attrs={"class": "form-control"}),
            "value_total": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def clean(self):
        cleaned = super().clean()
        voucher_type = cleaned.get("type")

        if voucher_type == Voucher.Type.MPV:
            if not cleaned.get("mpv_card"):
                self.add_error("mpv_card", "MPV musi mieć kartę.")
            if not cleaned.get("value_total"):
                self.add_error("value_total", "MPV musi mieć wartość początkową.")

        if voucher_type in [Voucher.Type.SPV, Voucher.Type.OLD]:
            if not cleaned.get("code"):
                self.add_error("code", "Voucher musi mieć kod.")

        if voucher_type == Voucher.Type.SPV:
            if not cleaned.get("service_name"):
                self.add_error("service_name", "SPV musi mieć nazwę usługi.")

        return cleaned
