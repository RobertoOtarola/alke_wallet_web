"""Views for the transactions app using CBVs."""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, FormView, DeleteView

from apps.accounts.models import Account
from core.exceptions import InsufficientFundsError, InvalidAmountError

from . import services
from .forms import TransactionForm
from .models import Transaction


class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


class TransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = "transactions/transaction_list.html"
    context_object_name = "transactions"

    def get_queryset(self):
        qs = Transaction.objects.select_related("account__user")
        if self.request.user.is_staff or self.request.user.is_superuser:
            return qs.all()
        return qs.filter(account__user=self.request.user)


class TransactionDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Transaction
    template_name = "transactions/transaction_detail.html"
    context_object_name = "tx"

    def test_func(self):
        tx = self.get_object()
        return self.request.user.is_staff or self.request.user.is_superuser or tx.account.user == self.request.user


class TransactionCreateView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    template_name = "transactions/transaction_form.html"
    form_class = TransactionForm

    def test_func(self):
        account = get_object_or_404(Account, pk=self.kwargs["account_pk"])
        if self.request.user.is_superuser:
            return True
        if self.request.user.is_staff:
            return False  # Staff cannot create
        return account.user == self.request.user

    def get_initial(self):
        return {"account_id": self.kwargs["account_pk"]}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["account"] = get_object_or_404(Account.objects.select_related("user"), pk=self.kwargs["account_pk"])
        return context

    def form_valid(self, form):
        account = get_object_or_404(Account.objects.select_related("user"), pk=self.kwargs["account_pk"])
        tx_type = form.cleaned_data["transaction_type"]
        amount = form.cleaned_data["amount"]
        description = form.cleaned_data.get("description", "")
        try:
            if tx_type == Transaction.TransactionType.DEPOSIT:
                tx = services.deposit(account, amount, description)
            else:
                tx = services.withdraw(account, amount, description)
            messages.success(
                self.request,
                f"{tx.get_transaction_type_display()} de ${amount:,.2f} registrada.",
            )
            return redirect("accounts:account_detail", pk=account.pk)
        except (InsufficientFundsError, InvalidAmountError) as exc:
            messages.error(self.request, str(exc))
            return self.form_invalid(form)
        except Exception as exc:
            messages.error(self.request, f"Error inesperado: {exc}")
            return self.form_invalid(form)


class TransactionDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Transaction
    template_name = "transactions/transaction_confirm_delete.html"

    def form_valid(self, form):
        tx = self.get_object()
        account_pk = tx.account_id
        services.delete_transaction(tx)
        messages.warning(
            self.request,
            "Transacción eliminada. El saldo de la cuenta NO fue revertido.",
        )
        return redirect("accounts:account_detail", pk=account_pk)
