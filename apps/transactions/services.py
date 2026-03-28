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
      2. Create Transaction record
      3. Update Account balance

    All steps are wrapped in a single atomic DB transaction.
    """
    _validate_amount(amount)

    with db_transaction.atomic():
        tx = Transaction.objects.create(
            account=account,
            amount=amount,
            transaction_type=Transaction.TransactionType.DEPOSIT,
            description=description,
        )
        Account.objects.filter(pk=account.pk).update(
            balance=account.balance + amount
        )
        account.refresh_from_db(fields=["balance"])

    return tx


def withdraw(account: Account, amount: Decimal, description: str = "") -> Transaction:
    """Withdraw *amount* from *account*.

    Steps:
      1. Validate amount > 0
      2. Validate sufficient balance
      3. Create Transaction record
      4. Update Account balance

    All steps are wrapped in a single atomic DB transaction.
    """
    _validate_amount(amount)

    # Re-fetch the balance inside the atomic block to avoid race conditions.
    with db_transaction.atomic():
        # Lock the row for the duration of the transaction.
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
    """Hard-delete a transaction record.

    NOTE: This does NOT reverse the corresponding balance change.
    Use only for data-cleanup purposes in development.
    """
    tx.delete()
