"""URL patterns for the transactions app."""

from django.urls import path

from . import views

app_name = "transactions"

urlpatterns = [
    path("", views.transaction_list, name="transaction_list"),
    path("create/<int:account_pk>/", views.transaction_create, name="transaction_create"),
    path("<int:pk>/", views.transaction_detail, name="transaction_detail"),
    path("<int:pk>/delete/", views.transaction_delete, name="transaction_delete"),
]
