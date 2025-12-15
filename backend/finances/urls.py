from django.urls import path

from finances.views import TransactionList, TransactionDetail, BalanceDetail, BalanceList, BalanceSumm, \
    ProcessFileUpload, RefreshExchangeRates, CurrencyList, get_losses, get_profits

urlpatterns = [
    path('transactions/<int:pk>/', TransactionDetail.as_view()),
    path('balance/', BalanceList.as_view()),
    path('balance/<int:pk>/', BalanceDetail.as_view()),

    path('balance/<int:pk>/transactions/', TransactionList.as_view()),
    path('balance/summ/', BalanceSumm.as_view()),

    path('import/', ProcessFileUpload.as_view()),
    path('exchange-rates/refresh/', RefreshExchangeRates.as_view()),
    path('currencies/', CurrencyList.as_view()),

    path('losses/', get_losses),
    path('profits/', get_profits)
]
