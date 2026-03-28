"""URL patterns for the accounts app."""

from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("", views.AccountListView.as_view(), name="account_list"),
    path("create/", views.AccountCreateView.as_view(), name="account_create"),
    path("<int:pk>/", views.AccountDetailView.as_view(), name="account_detail"),
    path("<int:pk>/edit/", views.AccountUpdateView.as_view(), name="account_update"),
    path("<int:pk>/delete/", views.AccountDeleteView.as_view(), name="account_delete"),
]
