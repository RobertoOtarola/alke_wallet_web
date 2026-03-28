"""Root URL configuration for Alke Wallet Web."""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", RedirectView.as_view(url="/users/", permanent=False), name="home"),
    path("users/", include("apps.users.urls", namespace="users")),
    path("accounts/", include("apps.accounts.urls", namespace="accounts")),
    path("transactions/", include("apps.transactions.urls", namespace="transactions")),
    path("", include("django.contrib.auth.urls")),
]
