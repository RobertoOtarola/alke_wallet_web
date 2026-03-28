"""User domain model."""

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import EmailValidator


class CustomUserManager(BaseUserManager):
    """Manager for Custom User using email as the unique identifier."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El email es obligatorio")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Represents a registered Alke Wallet user."""

    username = None
    name = models.CharField(
        max_length=150,
        verbose_name="Nombre completo",
    )
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator()],
        verbose_name="Correo electrónico",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de registro",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    objects = CustomUserManager()

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} <{self.email}>"
