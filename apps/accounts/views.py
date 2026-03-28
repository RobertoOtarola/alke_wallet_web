"""Views for the accounts app."""

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from . import services
from .forms import AccountForm, AccountUpdateForm
from .models import Account


def account_list(request):
    """GET /accounts/ — list all accounts."""
    accounts = Account.objects.select_related("user").all()
    return render(request, "accounts/account_list.html", {"accounts": accounts})


def account_detail(request, pk: int):
    """GET /accounts/<pk>/ — display a single account with its transactions."""
    account = get_object_or_404(Account.objects.select_related("user"), pk=pk)
    transactions = account.transactions.order_by("-created_at")
    return render(
        request,
        "accounts/account_detail.html",
        {"account": account, "transactions": transactions},
    )


def account_create(request):
    """GET + POST /accounts/create/ — create a new account for a user."""
    if request.method == "POST":
        form = AccountForm(request.POST)
        if form.is_valid():
            try:
                account = services.create_account(user=form.cleaned_data["user"])
                messages.success(request, f"Cuenta #{account.pk} creada exitosamente.")
                return redirect("accounts:account_detail", pk=account.pk)
            except Exception as exc:
                messages.error(request, str(exc))
    else:
        form = AccountForm()
    return render(request, "accounts/account_form.html", {"form": form, "title": "Nueva Cuenta"})


def account_update(request, pk: int):
    """GET + POST /accounts/<pk>/edit/ — toggle account active status."""
    account = get_object_or_404(Account, pk=pk)
    if request.method == "POST":
        form = AccountUpdateForm(request.POST, instance=account)
        if form.is_valid():
            form.save()
            messages.success(request, "Cuenta actualizada.")
            return redirect("accounts:account_detail", pk=account.pk)
    else:
        form = AccountUpdateForm(instance=account)
    return render(
        request,
        "accounts/account_form.html",
        {"form": form, "title": "Editar Cuenta", "account": account},
    )


def account_delete(request, pk: int):
    """GET + POST /accounts/<pk>/delete/ — confirm and delete an account."""
    account = get_object_or_404(Account, pk=pk)
    if request.method == "POST":
        services.delete_account(account)
        messages.success(request, "Cuenta eliminada.")
        return redirect("accounts:account_list")
    return render(request, "accounts/account_confirm_delete.html", {"account": account})
