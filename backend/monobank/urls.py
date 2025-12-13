from django.urls import path

from monobank.views import TokenView, MonobankBalanceList

urlpatterns = [
    path('token/', TokenView.as_view(), name='token'),
    path('balances/', MonobankBalanceList.as_view()),
]