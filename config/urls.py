"""Root URL configuration for Alke Wallet Web."""

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

def home_redirect(request):
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            return redirect("users:user_list")
        if hasattr(request.user, "account"):
            return redirect("accounts:account_detail", pk=request.user.account.pk)
    return redirect("login")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home_redirect, name="home"),
    path("users/", include("apps.users.urls", namespace="users")),
    path("accounts/", include("apps.accounts.urls", namespace="accounts")),
    path("transactions/", include("apps.transactions.urls", namespace="transactions")),
    path("", include("django.contrib.auth.urls")),
]
