from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .views import (APICreateAccount, APIBalanceAccount, APITransaction,
                    UserViewSet)

router_v1 = SimpleRouter()
router_v1.register(r'auth', UserViewSet, basename='auth')

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/accounts/create/', APICreateAccount.as_view()),
    path('v1/accounts/balance/', APIBalanceAccount.as_view()),
    path('v1/accounts/transaction/', APITransaction.as_view()),
]
