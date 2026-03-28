"""Integration tests for transaction views."""

from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import Account
from apps.transactions.models import Transaction
from apps.users.models import User


class TransactionCreateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="test@alke.cl",
            name="Test User",
            password="password123"
        )
        cls.account = Account.objects.create(user=cls.user, balance=Decimal("1000.00"))
        
    def setUp(self):
        # View uses standard authentication and messages, we should log in if needed. 
        # But looking at views.py, there might not be @login_required decorators? Let's assume standard behavior.
        self.client.force_login(self.user)

    def test_get_create_transaction_renders_form(self):
        url = reverse("transactions:transaction_create", kwargs={"account_pk": self.account.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "transactions/transaction_form.html")

    def test_post_deposit_creates_transaction_and_redirects(self):
        url = reverse("transactions:transaction_create", kwargs={"account_pk": self.account.pk})
        data = {
            "account_id": self.account.pk,
            "transaction_type": Transaction.TransactionType.DEPOSIT,
            "amount": "500.00",
            "description": "Depósito de prueba"
        }
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse("accounts:account_detail", kwargs={"pk": self.account.pk}))
        
        # Verify balance updated
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, Decimal("1500.00"))
        
        # Verify transaction created
        tx = Transaction.objects.last()
        self.assertEqual(tx.amount, Decimal("500.00"))
        self.assertEqual(tx.transaction_type, Transaction.TransactionType.DEPOSIT)

    def test_post_withdraw_creates_transaction_and_redirects(self):
        url = reverse("transactions:transaction_create", kwargs={"account_pk": self.account.pk})
        data = {
            "account_id": self.account.pk,
            "transaction_type": Transaction.TransactionType.WITHDRAW,
            "amount": "200.00",
            "description": "Retiro de prueba"
        }
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse("accounts:account_detail", kwargs={"pk": self.account.pk}))
        
        # Verify balance updated
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, Decimal("800.00"))

    def test_post_withdraw_insufficient_funds_shows_error(self):
        url = reverse("transactions:transaction_create", kwargs={"account_pk": self.account.pk})
        data = {
            "account_id": self.account.pk,
            "transaction_type": Transaction.TransactionType.WITHDRAW,
            "amount": "2000.00",
            "description": "Retiro fallido"
        }
        response = self.client.post(url, data)
        # Assuming messages framework handles this and re-renders form or redirects
        # Based on views.py, it renders form with messages if ValidationError, but views.py says:
        # messages.error(request, str(exc)) and then what? It falls through to render form!
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "transactions/transaction_form.html")
        
        # Balance untouched
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, Decimal("1000.00"))
