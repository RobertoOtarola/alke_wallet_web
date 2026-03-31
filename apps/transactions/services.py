"""Business logic for financial transactions.

All balance mutations MUST go through this service to guarantee atomicity
and correct validation ordering.
"""

from decimal import Decimal

from django.db import transaction as db_transaction

from core.exceptions import InsufficientFundsError, InvalidAmountError

from apps.accounts.models import Account
from .models import Transaction


def _validate_amount(amount: Decimal) -> None:
    if amount <= Decimal("0"):
        raise InvalidAmountError(amount)


def deposit(account: Account, amount: Decimal, description: str = "") -> Transaction:
    """Deposit *amount* into *account*.

    Steps:
      1. Validate amount > 0
      2. Lock the account row (``select_for_update``)
      3. Create Transaction record
      4. Update Account balance

    All steps are wrapped in a single atomic DB transaction.
    """
    _validate_amount(amount)

    with db_transaction.atomic():
        account_locked = Account.objects.select_for_update().get(pk=account.pk)

        tx = Transaction.objects.create(
            account=account_locked,
            amount=amount,
            transaction_type=Transaction.TransactionType.DEPOSIT,
            description=description,
        )
        Account.objects.filter(pk=account_locked.pk).update(
            balance=account_locked.balance + amount
        )
        account.refresh_from_db(fields=["balance"])

    return tx


def withdraw(account: Account, amount: Decimal, description: str = "") -> Transaction:
    """Withdraw *amount* from *account*.

    Steps:
      1. Validate amount > 0
      2. Lock the account row (``select_for_update``)
      3. Validate sufficient balance
      4. Create Transaction record
      5. Update Account balance

    All steps are wrapped in a single atomic DB transaction.
    """
    _validate_amount(amount)

    with db_transaction.atomic():
        account_locked = Account.objects.select_for_update().get(pk=account.pk)

        if account_locked.balance < amount:
            raise InsufficientFundsError(
                balance=float(account_locked.balance),
                amount=float(amount),
            )

        tx = Transaction.objects.create(
            account=account_locked,
            amount=amount,
            transaction_type=Transaction.TransactionType.WITHDRAW,
            description=description,
        )
        Account.objects.filter(pk=account_locked.pk).update(
            balance=account_locked.balance - amount
        )
        account.refresh_from_db(fields=["balance"])

    return tx


def delete_transaction(tx: Transaction) -> None:
    """Delete a transaction record.

    Only available when ``DEBUG=True`` (development environment).
    In production, transactions are immutable by design — this prevents
    audit-trail corruption.

    NOTE: This does NOT reverse the corresponding balance change.
    """
    from django.conf import settings

    if not settings.DEBUG:
        raise PermissionError(
            "Las transacciones no se pueden eliminar en producción."
        )
    tx.delete()
