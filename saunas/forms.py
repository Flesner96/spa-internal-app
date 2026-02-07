from django import forms
from .models import SaunaSession
from django.forms import formset_factory


class SaunaAttendanceForm(forms.ModelForm):
    class Meta:
        model = SaunaSession
        fields = ["women", "men"]


class ParsedSessionForm(forms.Form):
    start_time = forms.TimeField()
    session_name = forms.CharField(max_length=200)
    sauna_name = forms.CharField(max_length=100, required=False)


ParsedSessionFormSet = formset_factory(
    ParsedSessionForm,
    extra=0,
)
