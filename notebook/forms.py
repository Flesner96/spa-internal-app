from django import forms
from .models import AreaMessage, AreaMessageReply

class AreaMessageForm(forms.ModelForm):
    class Meta:
        model = AreaMessage
        fields = ["content", "attachment"]

        widgets = {
            "content": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Dodaj ważną informację dla zespołu..."
            }),
            "attachment": forms.ClearableFileInput(attrs={
                "class": "form-control"
            }),
        }


class AreaMessageReplyForm(forms.ModelForm):
    class Meta:
        model = AreaMessageReply
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Odpowiedź..."
            })
        }