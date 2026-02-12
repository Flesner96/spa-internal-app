from django import forms
from .constants import DENOMINATIONS


class CashCountForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for key in DENOMINATIONS.keys():
            self.fields[key] = forms.IntegerField(
                required=False,
                min_value=0,
                label=key,
                widget=forms.NumberInput(attrs={
                    "class": "form-control",
                    "placeholder": "0",
                })
            )
