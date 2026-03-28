"""Forms for the users app."""

from django import forms

from .models import User


class UserForm(forms.ModelForm):
    """Form used for both creating and updating a User."""

    password = forms.CharField(
        widget=forms.PasswordInput(render_value=False),
        label="Contraseña",
        min_length=8,
        help_text="Mínimo 8 caracteres.",
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(),
        label="Confirmar contraseña",
    )

    class Meta:
        model = User
        fields = ["name", "email", "password"]

    def clean(self):
        cleaned = super().clean()
        pwd = cleaned.get("password")
        confirm = cleaned.get("confirm_password")
        if pwd and confirm and pwd != confirm:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned


class UserUpdateForm(forms.ModelForm):
    """Form for editing a user — password change is optional."""

    class Meta:
        model = User
        fields = ["name", "email", "is_active"]
