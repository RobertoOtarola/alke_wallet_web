"""URL patterns for the accounts app."""

from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("", views.account_list, name="account_list"),
    path("create/", views.account_create, name="account_create"),
    path("<int:pk>/", views.account_detail, name="account_detail"),
    path("<int:pk>/edit/", views.account_update, name="account_update"),
    path("<int:pk>/delete/", views.account_delete, name="account_delete"),
]
