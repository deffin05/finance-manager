from django.urls import path

from monobank.views import TokenView, MonobankBalanceList, verify_token, MonobankBalanceWatch

urlpatterns = [
    path('token/', TokenView.as_view(), name='token'),
    path('balances/', MonobankBalanceList.as_view()),
    path('verify/', verify_token),
    path('balances/<int:pk>/', MonobankBalanceWatch.as_view())
]
