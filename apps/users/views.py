"""Views for the users app.

Pattern: Template → View → Service → ORM → Database.
Views only coordinate HTTP; all business logic lives in services.py.
"""

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from . import services
from .forms import UserForm, UserUpdateForm
from .models import User


def user_list(request):
    """GET /users/ — list all users."""
    users = User.objects.all()
    return render(request, "users/user_list.html", {"users": users})


def user_detail(request, pk: int):
    """GET /users/<pk>/ — display a single user."""
    user = get_object_or_404(User, pk=pk)
    return render(request, "users/user_detail.html", {"user": user})


def user_create(request):
    """GET + POST /users/create/ — create a new user."""
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            try:
                services.create_user(
                    name=form.cleaned_data["name"],
                    email=form.cleaned_data["email"],
                    raw_password=form.cleaned_data["password"],
                )
                messages.success(request, "Usuario creado exitosamente.")
                return redirect("users:user_list")
            except Exception as exc:
                messages.error(request, f"Error al crear usuario: {exc}")
    else:
        form = UserForm()
    return render(request, "users/user_form.html", {"form": form, "title": "Nuevo Usuario"})


def user_update(request, pk: int):
    """GET + POST /users/<pk>/edit/ — update an existing user."""
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            try:
                services.update_user(
                    user=user,
                    name=form.cleaned_data["name"],
                    email=form.cleaned_data["email"],
                    is_active=form.cleaned_data["is_active"],
                )
                messages.success(request, "Usuario actualizado exitosamente.")
                return redirect("users:user_detail", pk=user.pk)
            except Exception as exc:
                messages.error(request, f"Error al actualizar: {exc}")
    else:
        form = UserUpdateForm(instance=user)
    return render(request, "users/user_form.html", {"form": form, "title": "Editar Usuario", "user": user})


def user_delete(request, pk: int):
    """GET + POST /users/<pk>/delete/ — confirm and delete a user."""
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        services.delete_user(user)
        messages.success(request, "Usuario eliminado.")
        return redirect("users:user_list")
    return render(request, "users/user_confirm_delete.html", {"user": user})
