from django import forms
from .models import ShiftCloseReport


class ShiftCloseReportForm(forms.ModelForm):

    shift_type = forms.ChoiceField(
        choices=ShiftCloseReport.ShiftType.choices,
        widget=forms.RadioSelect,
    )

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
            "notes": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        prefill_cash = kwargs.pop("prefill_cash", None)
        super().__init__(*args, **kwargs)

        if prefill_cash:
            self.fields["closing_cash"].initial = prefill_cash