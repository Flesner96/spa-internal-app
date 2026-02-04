from django import forms
from .models import User, Role, UserRole, AreaMessage
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model

class UserCreateForm(forms.ModelForm):
    roles = forms.ModelMultipleChoiceField(
        queryset=Role.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Role"
    )

    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "phone",
            "area",
            "is_active",
        ]

    def clean_roles(self):
        roles = self.cleaned_data.get("roles")
        if not roles or roles.count() == 0:
            raise forms.ValidationError("Musisz przypisać co najmniej jedną rolę.")
        return roles

    def save(self, commit=True):
        user = super().save(commit=False)
        
        user.set_password(User.objects.make_random_password())
        if commit:
            user.save()
            for role in self.cleaned_data["roles"]:
                UserRole.objects.create(user=user, role=role)
        return user


User = get_user_model()

# forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm

class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "Email"
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Hasło"
        })
    )


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone"]

        widgets = {
            "first_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Imię"
            }),
            "last_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nazwisko"
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Email"
            }),
            "phone": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Numer telefonu"
            }),
        }



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