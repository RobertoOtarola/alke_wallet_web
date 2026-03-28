"""Forms for the transactions app."""

from decimal import Decimal

from django import forms

from .models import Transaction


class TransactionForm(forms.Form):
    """Generic form for creating a deposit or withdrawal."""

    account_id = forms.IntegerField(widget=forms.HiddenInput())
    amount = forms.DecimalField(
        max_digits=14,
        decimal_places=2,
        min_value=Decimal("0.01"),
        label="Monto",
        help_text="Ingresa el monto de la operación.",
    )
    transaction_type = forms.ChoiceField(
        choices=Transaction.TransactionType.choices,
        label="Tipo de operación",
    )
    description = forms.CharField(
        max_length=255,
        required=False,
        label="Descripción (opcional)",
    )
