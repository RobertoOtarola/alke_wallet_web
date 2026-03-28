"""Business logic for account management."""

from apps.users.models import User
from core.exceptions import AccountNotFoundError

from .models import Account


def create_account(user: User) -> Account:
    """Create a new Account for the given User.

    Raises ``ValueError`` if the user already has an account.
    """
    if Account.objects.filter(user=user).exists():
        raise ValueError(f"El usuario {user.email} ya tiene una cuenta.")
    account = Account(user=user)
    account.full_clean()
    account.save()
    return account


def get_account_for_user(user: User) -> Account:
    """Return the Account associated with *user* or raise AccountNotFoundError."""
    try:
        return Account.objects.get(user=user)
    except Account.DoesNotExist:
        raise AccountNotFoundError(f"No se encontró cuenta para {user.email}.")


def deactivate_account(account: Account) -> Account:
    """Set account as inactive (soft disable)."""
    account.is_active = False
    account.save(update_fields=["is_active"])
    return account


def activate_account(account: Account) -> Account:
    """Re-enable a previously deactivated account."""
    account.is_active = True
    account.save(update_fields=["is_active"])
    return account


def delete_account(account: Account) -> None:
    """Hard-delete an account record."""
    account.delete()
