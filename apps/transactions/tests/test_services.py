"""Unit tests for the transactions service layer — core financial logic."""

from decimal import Decimal

from django.test import TestCase

from apps.accounts.models import Account
from apps.transactions import services
from apps.transactions.models import Transaction
from apps.users.models import User
from core.exceptions import InsufficientFundsError, InvalidAmountError


def _setup():
    user = User.objects.create(name="U", email="u@alke.cl", password="x")
    account = Account.objects.create(user=user, balance=Decimal("1000.00"))
    return account


class DepositServiceTest(TestCase):

    def setUp(self):
        self.account = _setup()

    def test_deposit_increases_balance(self):
        services.deposit(self.account, Decimal("200.00"))
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, Decimal("1200.00"))

    def test_deposit_creates_transaction_record(self):
        tx = services.deposit(self.account, Decimal("50.00"), description="Pago")
        self.assertEqual(tx.transaction_type, Transaction.TransactionType.DEPOSIT)
        self.assertEqual(tx.amount, Decimal("50.00"))
        self.assertEqual(tx.description, "Pago")

    def test_deposit_zero_raises_invalid_amount(self):
        with self.assertRaises(InvalidAmountError):
            services.deposit(self.account, Decimal("0"))

    def test_deposit_negative_raises_invalid_amount(self):
        with self.assertRaises(InvalidAmountError):
            services.deposit(self.account, Decimal("-100"))


class WithdrawServiceTest(TestCase):

    def setUp(self):
        self.account = _setup()

    def test_withdraw_decreases_balance(self):
        services.withdraw(self.account, Decimal("300.00"))
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, Decimal("700.00"))

    def test_withdraw_creates_transaction_record(self):
        tx = services.withdraw(self.account, Decimal("100.00"))
        self.assertEqual(tx.transaction_type, Transaction.TransactionType.WITHDRAW)

    def test_withdraw_exact_balance_succeeds(self):
        services.withdraw(self.account, Decimal("1000.00"))
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, Decimal("0.00"))

    def test_withdraw_exceeding_balance_raises_error(self):
        with self.assertRaises(InsufficientFundsError):
            services.withdraw(self.account, Decimal("1000.01"))

    def test_withdraw_zero_raises_invalid_amount(self):
        with self.assertRaises(InvalidAmountError):
            services.withdraw(self.account, Decimal("0"))
