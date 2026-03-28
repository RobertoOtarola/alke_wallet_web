"""Forms for the accounts app."""

from django import forms

from .models import Account


class AccountForm(forms.ModelForm):
    """Used to create a new Account linked to an existing User."""

    class Meta:
        model = Account
        fields = ["user"]


class AccountUpdateForm(forms.ModelForm):
    """Allows toggling the active status of an Account."""

    class Meta:
        model = Account
        fields = ["is_active"]
