"""User domain model."""

from django.db import models
from django.core.validators import EmailValidator


class User(models.Model):
    """Represents a registered Alke Wallet user."""

    name = models.CharField(
        max_length=150,
        verbose_name="Nombre completo",
    )
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator()],
        verbose_name="Correo electrónico",
    )
    # Stores a bcrypt/PBKDF2 hash — never a plaintext password.
    password = models.CharField(
        max_length=255,
        verbose_name="Contraseña (hash)",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Activo",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de registro",
    )

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} <{self.email}>"
