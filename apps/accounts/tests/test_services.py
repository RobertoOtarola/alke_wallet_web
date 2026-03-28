"""Unit tests for the accounts service layer."""

from django.test import TestCase

from apps.accounts import services
from apps.accounts.models import Account
from apps.users.models import User
from core.exceptions import AccountNotFoundError


def _make_user(email="u@alke.cl"):
    return User.objects.create(name="User", email=email, password="x")


class CreateAccountServiceTest(TestCase):

    def test_creates_account_with_zero_balance(self):
        user = _make_user()
        account = services.create_account(user)
        self.assertIsInstance(account, Account)
        self.assertEqual(account.balance, 0)
        self.assertTrue(account.is_active)

    def test_duplicate_account_raises_error(self):
        user = _make_user()
        services.create_account(user)
        with self.assertRaises(ValueError):
            services.create_account(user)


class GetAccountServiceTest(TestCase):

    def test_returns_account(self):
        user = _make_user()
        created = services.create_account(user)
        fetched = services.get_account_for_user(user)
        self.assertEqual(created.pk, fetched.pk)

    def test_raises_error_when_not_found(self):
        user = _make_user()
        with self.assertRaises(AccountNotFoundError):
            services.get_account_for_user(user)
