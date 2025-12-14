from django.urls import path

from finances.views import TransactionList, TransactionDetail, BalanceDetail, BalanceList

urlpatterns = [
    path('transactions/<int:pk>/', TransactionDetail.as_view()),
    path('balance/', BalanceList.as_view()),
    path('balance/<int:pk>/', BalanceDetail.as_view()),

    path('balance/<int:pk>/transactions/', TransactionList.as_view()),
]
