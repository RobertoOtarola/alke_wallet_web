"""Account domain model."""

from django.db import models

from apps.users.models import User


class Account(models.Model):
    """A financial account owned by a single User.

    One user can have exactly one account (OneToOneField ensures uniqueness
    at the database level).
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="account",
        verbose_name="Usuario",
    )
    balance = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="Saldo",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Cuenta activa",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de apertura",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Última actualización",
    )

    class Meta:
        verbose_name = "Cuenta"
        verbose_name_plural = "Cuentas"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Cuenta #{self.pk} — {self.user.name} (${self.balance:,.2f})"
