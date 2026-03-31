"""Views for the accounts app using CBVs."""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, FormView, UpdateView, DeleteView

from core.exceptions import AlkeWalletError

from . import services
from .forms import AccountForm, AccountUpdateForm
from .models import Account

class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

class AccountListView(LoginRequiredMixin, ListView):
    model = Account
    template_name = "accounts/account_list.html"
    context_object_name = "accounts"

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return Account.objects.select_related("user").all()
        return Account.objects.select_related("user").filter(user=self.request.user)

class AccountDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Account
    template_name = "accounts/account_detail.html"
    context_object_name = "account"

    def test_func(self):
        account = self.get_object()
        return self.request.user.is_staff or self.request.user.is_superuser or account.user == self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["transactions"] = self.object.transactions.order_by("-created_at")
        return context

class AccountCreateView(LoginRequiredMixin, StaffRequiredMixin, FormView):
    template_name = "accounts/account_form.html"
    form_class = AccountForm

    def form_valid(self, form):
        try:
            account = services.create_account(user=form.cleaned_data["user"])
            messages.success(self.request, f"Cuenta #{account.pk} creada exitosamente.")
            return redirect("accounts:account_detail", pk=account.pk)
        except (ValueError, AlkeWalletError) as exc:
            messages.error(self.request, str(exc))
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Nueva Cuenta"
        return context

class AccountUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Account
    form_class = AccountUpdateForm
    template_name = "accounts/account_form.html"

    def form_valid(self, form):
        messages.success(self.request, "Cuenta actualizada.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("accounts:account_detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Editar Cuenta"
        return context

class AccountDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Account
    template_name = "accounts/account_confirm_delete.html"
    success_url = reverse_lazy("accounts:account_list")

    def form_valid(self, form):
        services.delete_account(self.get_object())
        messages.success(self.request, "Cuenta eliminada.")
        return redirect(self.success_url)
