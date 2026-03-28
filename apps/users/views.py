"""Views for the users app using CBVs."""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, FormView, DeleteView

from . import services
from .forms import UserForm, UserUpdateForm
from .models import User

class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

class UserListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = User
    template_name = "users/user_list.html"
    context_object_name = "users"

class UserDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = User
    template_name = "users/user_detail.html"
    context_object_name = "user"

    def test_func(self):
        user = self.get_object()
        return self.request.user.is_staff or self.request.user.is_superuser or self.request.user == user

class UserCreateView(FormView):
    template_name = "users/user_form.html"
    form_class = UserForm

    def form_valid(self, form):
        try:
            services.create_user(
                name=form.cleaned_data["name"],
                email=form.cleaned_data["email"],
                raw_password=form.cleaned_data["password"],
            )
            messages.success(self.request, "Usuario creado exitosamente. Ya puedes iniciar sesión.")
            return redirect("login")
        except Exception as exc:
            messages.error(self.request, f"Error al crear usuario: {exc}")
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Nuevo Usuario"
        return context

class UserUpdateView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    template_name = "users/user_form.html"
    form_class = UserUpdateForm

    def test_func(self):
        user = get_object_or_404(User, pk=self.kwargs["pk"])
        return self.request.user.is_staff or self.request.user.is_superuser or self.request.user == user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = get_object_or_404(User, pk=self.kwargs["pk"])
        return kwargs

    def form_valid(self, form):
        user = get_object_or_404(User, pk=self.kwargs["pk"])
        is_active = form.cleaned_data["is_active"] if self.request.user.is_staff else user.is_active
        try:
            services.update_user(
                user=user,
                name=form.cleaned_data["name"],
                email=form.cleaned_data["email"],
                is_active=is_active,
            )
            messages.success(self.request, "Usuario actualizado exitosamente.")
            return redirect("users:user_detail", pk=user.pk)
        except Exception as exc:
            messages.error(self.request, f"Error al actualizar: {exc}")
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        user = get_object_or_404(User, pk=self.kwargs["pk"])
        context = super().get_context_data(**kwargs)
        context["title"] = "Editar Usuario"
        context["user"] = user
        return context

class UserDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = User
    template_name = "users/user_confirm_delete.html"
    success_url = reverse_lazy("users:user_list")

    def form_valid(self, form):
        services.delete_user(self.get_object())
        messages.success(self.request, "Usuario eliminado.")
        return redirect(self.success_url)
