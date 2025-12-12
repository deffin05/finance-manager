from rest_framework import generics

from finances.serializers import TransactionSerializer, BalanceSerializer
from finances.models import Transaction, Balance
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 250

class TransactionList(generics.ListCreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated] #Only allow authorized users so that we can gracefully return 403 if an anonymous user hits the endpoint
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = Transaction.objects.all().filter(user = self.request.user) # Filter transactions by the authenticated user

        #sorting logic

        #TODO: sort by amount normalized currency values once we have that implemented
        sort_by = self.request.query_params.get('sort_by')
        order = self.request.query_params.get('order') #'asc'/'desc'
        allowed_sort_fields = ['date', 'amount']
        allowed_order_fields = ['asc', 'desc']

        if not sort_by or sort_by not in allowed_sort_fields: sort_by = 'date'
        if not order or order not in allowed_order_fields: order = 'desc'

        if order == 'desc': sort_by = '-'+sort_by

        queryset = queryset.order_by(sort_by)
        return queryset 

    def perform_create(self, serializer): # Override to update balance on transaction creation
        transaction = serializer.save(user=self.request.user) # Ensure the transaction is linked to the authenticated user
        balance, created = Balance.objects.get_or_create(
            user=transaction.user,
            defaults={'amount': 0},
            currency=transaction.currency
        )
        balance.amount += transaction.amount
        balance.save()

class TransactionDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated] 

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        instance = serializer.instance
        old_transaction = Transaction.objects.get(pk=instance.pk)
        transaction = serializer.save()
        
        balance = Balance.objects.get(
            user = transaction.user,
            currency=transaction.currency
        )
        
        balance.amount -= old_transaction.amount
        balance.amount += transaction.amount
        balance.save()
        
    def perform_destroy(self, instance):
        balance = Balance.objects.get(
            user = instance.user,
            currency = instance.currency
        )
        
        balance.amount -= instance.amount
        balance.save()
        instance.delete()


class BalanceList(generics.ListCreateAPIView):
    serializer_class = BalanceSerializer
    permission_classes = [IsAuthenticated] 

    def get_queryset(self):
        return Balance.objects.filter(user=self.request.user)
    def perform_create(self, serializer): #override to set user on balance creation
        serializer.save(user=self.request.user)

class BalanceDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Balance.objects.all()
    permission_classes = [IsAuthenticated] 

    serializer_class = BalanceSerializer
    def get_queryset(self):
        return Balance.objects.filter(user=self.request.user)