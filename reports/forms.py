from django import forms
from .models import ShiftCloseReport


class ShiftCloseReportForm(forms.ModelForm):

    class Meta:
        model = ShiftCloseReport
        fields = [
            "shift_type",
            "closing_cash",
            "cash_removed",
            "laundry_delivery",
            "notes",
        ]
        widgets = {
            "laundry_delivery": forms.CheckboxInput(attrs={
                "class": "form-check-input",
                "id": "id_laundry_delivery"
            }),
            "closing_cash": forms.NumberInput(attrs={
                "class": "form-control"
            }),
            "cash_removed": forms.NumberInput(attrs={
                "class": "form-control"
            }),
            "notes": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4
            }),
        }

    def __init__(self, *args, **kwargs):
        prefill_cash = kwargs.pop("prefill_cash", None)
        super().__init__(*args, **kwargs)

        if prefill_cash:
            self.fields["closing_cash"].initial = prefill_cash