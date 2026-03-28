"""URL patterns for the transactions app."""

from django.urls import path

from . import views

app_name = "transactions"

urlpatterns = [
    path("", views.TransactionListView.as_view(), name="transaction_list"),
    path("create/<int:account_pk>/", views.TransactionCreateView.as_view(), name="transaction_create"),
    path("<int:pk>/", views.TransactionDetailView.as_view(), name="transaction_detail"),
    path("<int:pk>/delete/", views.TransactionDeleteView.as_view(), name="transaction_delete"),
]
