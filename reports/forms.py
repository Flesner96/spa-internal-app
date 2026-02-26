from django import forms
from .models import ShiftCloseReport
from django.utils import timezone


class ShiftCloseReportForm(forms.ModelForm):

    class Meta:
        model = ShiftCloseReport
        fields = [
            "shift_date",
            "shift_type",
            "closing_cash",
            "cash_removed",
            "laundry_delivery",
            "notes",
        ]
        widgets = {
            "shift_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        prefill_cash = kwargs.pop("prefill_cash", None)
        super().__init__(*args, **kwargs)

        if not self.instance.pk:
            self.fields["shift_date"].initial = timezone.localdate()

        if prefill_cash:
            self.fields["closing_cash"].initial = prefill_cash