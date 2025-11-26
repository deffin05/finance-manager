from rest_framework import generics

from finances.serializers import TransactionSerializer, BalanceSerializer
from finances.models import Transaction, Balance


class TransactionList(generics.ListCreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def perform_create(self, serializer):
        transaction = serializer.save()
        balance, created = Balance.objects.get_or_create(
            user=transaction.user,
            defaults={'amount': 0},
            currency=transaction.currency
        )
        balance.amount += transaction.amount
        balance.save()

class TransactionDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer


class BalanceCreate(generics.CreateAPIView):
    serializer_class = BalanceSerializer


class BalanceDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Balance.objects.all()
    serializer_class = BalanceSerializer
