"""Shared validators used across all apps."""

from decimal import Decimal

from django.core.exceptions import ValidationError


def validate_positive_amount(value: Decimal) -> None:
    """Ensure a monetary amount is strictly positive."""
    if value <= Decimal("0"):
        raise ValidationError(
            "El monto debe ser un valor positivo mayor a cero.",
            code="non_positive_amount",
        )
