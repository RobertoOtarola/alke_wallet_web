"""Concurrency tests for the transactions service layer.

Uses ``TransactionTestCase`` (not ``TestCase``) because threads each
need their own DB connection, and Django's ``TestCase`` wraps everything
in a single transaction that other threads cannot see.

These tests exercise ``select_for_update()`` which requires a database
that supports row-level locking (PostgreSQL). SQLite serialises writes
at the connection level and does not support ``SELECT ... FOR UPDATE``,
so these tests are automatically skipped when running against SQLite.
"""

import threading
from decimal import Decimal

from django.db import connection
from django.test import TransactionTestCase, skipUnlessDBFeature

from apps.accounts.models import Account
from apps.transactions import services
from apps.users.models import User
from core.exceptions import InsufficientFundsError


@skipUnlessDBFeature("has_select_for_update")
class ConcurrentWithdrawTest(TransactionTestCase):
    """Two simultaneous withdrawals must never overdraft the account."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="concurrent@alke.cl",
            name="Concurrent User",
            password="testpass123",
        )
        self.account = Account.objects.create(
            user=self.user, balance=Decimal("100.00")
        )

    def test_concurrent_withdrawals_do_not_overdraft(self):
        """
        If two threads each try to withdraw $80 from a $100 account,
        exactly one must fail with ``InsufficientFundsError`` and the
        final balance must never be negative.
        """
        errors: list[str] = []

        def do_withdraw():
            try:
                services.withdraw(self.account, Decimal("80.00"))
            except InsufficientFundsError:
                errors.append("insufficient")

        t1 = threading.Thread(target=do_withdraw)
        t2 = threading.Thread(target=do_withdraw)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        self.account.refresh_from_db()
        self.assertGreaterEqual(
            self.account.balance,
            Decimal("0"),
            "Balance must never go negative under concurrent withdrawals.",
        )
        self.assertEqual(
            len(errors), 1, "Exactly one withdrawal should fail."
        )


@skipUnlessDBFeature("has_select_for_update")
class ConcurrentDepositTest(TransactionTestCase):
    """Two simultaneous deposits must both succeed without losing money."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="deposit@alke.cl",
            name="Deposit User",
            password="testpass123",
        )
        self.account = Account.objects.create(
            user=self.user, balance=Decimal("0.00")
        )

    def test_concurrent_deposits_sum_correctly(self):
        """
        Two concurrent deposits of $500 each on a $0 account must
        result in exactly $1000. No deposit should be lost.
        """
        def do_deposit():
            services.deposit(self.account, Decimal("500.00"))

        t1 = threading.Thread(target=do_deposit)
        t2 = threading.Thread(target=do_deposit)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        self.account.refresh_from_db()
        self.assertEqual(
            self.account.balance,
            Decimal("1000.00"),
            "Two concurrent $500 deposits must result in $1000.",
        )
