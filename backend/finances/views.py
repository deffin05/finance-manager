from rest_framework import generics

from finances.serializers import TransactionSerializer, BalanceSerializer
from finances.models import Transaction, Balance


class TransactionList(generics.ListCreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user) # Filter transactions by the authenticated user

    def perform_create(self, serializer): # Override to update balance on transaction creation
        transaction = serializer.save()
        balance, created = Balance.objects.get_or_create(
            user=transaction.user,
            defaults={'amount': 0},
            currency=transaction.currency
        )
        balance.amount += transaction.amount
        balance.save()

class TransactionDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TransactionSerializer
    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

class BalanceCreate(generics.CreateAPIView):
    serializer_class = BalanceSerializer

    def get_queryset(self):
        return Balance.objects.filter(user=self.request.user)
    def perform_create(self, serializer): #override to set user on balance creation
        serializer.save(user=self.request.user)

class BalanceDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Balance.objects.all()
    serializer_class = BalanceSerializer
    def get_queryset(self):
        return Balance.objects.filter(user=self.request.user)