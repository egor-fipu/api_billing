from django.urls import path

from .views import APICreateAccount, APIBalanceAccount, APITransaction

urlpatterns = [
    path('v1/accounts/create/', APICreateAccount.as_view()),
    path('v1/accounts/balance/', APIBalanceAccount.as_view()),
    path('v1/accounts/transaction/', APITransaction.as_view()),
]
