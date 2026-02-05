from django import forms
from .models import SaunaSession

class SaunaAttendanceForm(forms.ModelForm):
    class Meta:
        model = SaunaSession
        fields = ["women", "men"]

