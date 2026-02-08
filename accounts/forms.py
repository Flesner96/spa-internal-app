from django import forms
from .models import User, Role, UserRole
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
import secrets


User = get_user_model()

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
        if not roles:
            raise forms.ValidationError(
                "Musisz przypisać co najmniej jedną rolę."
            )
        return roles

    def save(self, commit=True):
        user = super().save(commit=False)

        temp_password = secrets.token_urlsafe(8)
        user.set_password(temp_password)
        user.must_change_password = True

        if commit:
            user.save()

            UserRole.objects.filter(user=user).delete()

            for role in self.cleaned_data["roles"]:
                UserRole.objects.create(user=user, role=role)

        return user, temp_password


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