"""Transaction domain model."""

from django.db import models

from apps.accounts.models import Account
from core.validators import validate_positive_amount


class Transaction(models.Model):
    """Records a single financial movement on an Account."""

    class TransactionType(models.TextChoices):
        DEPOSIT = "DEPOSIT", "Depósito"
        WITHDRAW = "WITHDRAW", "Retiro"

    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="transactions",
        verbose_name="Cuenta",
    )
    amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        validators=[validate_positive_amount],
        verbose_name="Monto",
    )
    transaction_type = models.CharField(
        max_length=10,
        choices=TransactionType.choices,
        verbose_name="Tipo",
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Descripción",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha",
    )

    class Meta:
        verbose_name = "Transacción"
        verbose_name_plural = "Transacciones"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return (
            f"{self.get_transaction_type_display()} ${self.amount:,.2f} "
            f"— Cuenta #{self.account_id}"
        )
