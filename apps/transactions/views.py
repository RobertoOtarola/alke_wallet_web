"""Views for the transactions app."""

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.models import Account
from core.exceptions import InsufficientFundsError, InvalidAmountError

from . import services
from .forms import TransactionForm
from .models import Transaction


def transaction_list(request):
    """GET /transactions/ — list all transactions across all accounts."""
    transactions = Transaction.objects.select_related("account__user").all()
    return render(
        request,
        "transactions/transaction_list.html",
        {"transactions": transactions},
    )


def transaction_detail(request, pk: int):
    """GET /transactions/<pk>/ — display a single transaction."""
    tx = get_object_or_404(
        Transaction.objects.select_related("account__user"), pk=pk
    )
    return render(request, "transactions/transaction_detail.html", {"tx": tx})


def transaction_create(request, account_pk: int):
    """GET + POST /transactions/create/<account_pk>/ — create deposit or withdrawal."""
    account = get_object_or_404(Account.objects.select_related("user"), pk=account_pk)

    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            tx_type = form.cleaned_data["transaction_type"]
            amount = form.cleaned_data["amount"]
            description = form.cleaned_data.get("description", "")
            try:
                if tx_type == Transaction.TransactionType.DEPOSIT:
                    tx = services.deposit(account, amount, description)
                else:
                    tx = services.withdraw(account, amount, description)
                messages.success(
                    request,
                    f"{tx.get_transaction_type_display()} de ${amount:,.2f} registrada.",
                )
                return redirect("accounts:account_detail", pk=account.pk)
            except (InsufficientFundsError, InvalidAmountError) as exc:
                messages.error(request, str(exc))
            except Exception as exc:
                messages.error(request, f"Error inesperado: {exc}")
    else:
        form = TransactionForm(initial={"account_id": account.pk})

    return render(
        request,
        "transactions/transaction_form.html",
        {"form": form, "account": account},
    )


def transaction_delete(request, pk: int):
    """GET + POST /transactions/<pk>/delete/ — confirm and delete a transaction."""
    tx = get_object_or_404(Transaction, pk=pk)
    account_pk = tx.account_id
    if request.method == "POST":
        services.delete_transaction(tx)
        messages.warning(
            request,
            "Transacción eliminada. El saldo de la cuenta NO fue revertido.",
        )
        return redirect("accounts:account_detail", pk=account_pk)
    return render(
        request,
        "transactions/transaction_confirm_delete.html",
        {"tx": tx},
    )
