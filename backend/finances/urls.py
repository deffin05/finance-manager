from django.urls import path

from finances.views import TransactionList, TransactionDetail, BalanceDetail, BalanceCreate

urlpatterns = [
    path('transactions/', TransactionList.as_view()),
    path('transactions/<int:pk>/', TransactionDetail.as_view()),
    path('balance/', BalanceCreate.as_view()),
    path('balance/<int:pk>/', BalanceDetail.as_view()),
]