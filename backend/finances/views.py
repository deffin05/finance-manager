from datetime import timedelta

from django.http.response import Http404
from django.utils import timezone
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response

from finances.serializers import TransactionSerializer, BalanceSerializer, FileUploadSerializer, CurrencySerializer
from finances.models import Transaction, Balance, Currency

from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import ValidationError

from finances.tasks import import_transaction_file, fetch_exchange_rates, fetch_crypto_rates
from monobank.models import MonobankUser, MonobankBalance
from monobank.views import fetch_monobank_report


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 250


class TransactionList(generics.ListCreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [
        IsAuthenticated]  # Only allow authorized users so that we can gracefully return 403 if an anonymous user hits the endpoint
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        balance_id = self.kwargs["pk"]
        balance = Balance.objects.get(pk=balance_id)

        if not balance or not (balance.user == self.request.user):
            raise Http404

        queryset = Transaction.objects.all().filter(balance=balance)

        # sorting logic

        # TODO: sort by amount normalized currency values once we have that implemented
        sort_by = self.request.query_params.get('sort_by')
        order = self.request.query_params.get('order')  # 'asc'/'desc'
        allowed_sort_fields = ['date', 'amount']
        allowed_order_fields = ['asc', 'desc']

        if not sort_by or sort_by not in allowed_sort_fields: sort_by = 'date'
        if not order or order not in allowed_order_fields: order = 'desc'

        if order == 'desc': sort_by = '-' + sort_by

        queryset = queryset.order_by(sort_by)
        return queryset

    def perform_create(self, serializer):  # Override to update balance on transaction creation
        balance_id = self.kwargs["pk"]
        balance = Balance.objects.get(pk=balance_id)
        if balance and balance.user != self.request.user:  # Ensure the transaction is linked to the authenticated user
            raise ValidationError({"balance": "You do not own this balance."})
        transaction = serializer.save(user=self.request.user, balance=balance)
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
        old_balance = old_transaction.balance
        transaction = serializer.save()

        balance = transaction.balance

        old_balance.amount -= old_transaction.amount
        old_balance.save()
        balance.refresh_from_db()

        balance.amount += transaction.amount
        balance.save()

    def perform_destroy(self, instance):
        balance = instance.balance

        balance.amount -= instance.amount
        balance.save()
        instance.delete()


class BalanceList(generics.ListCreateAPIView):
    serializer_class = BalanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        mono_user = MonobankUser.objects.filter(user=self.request.user).first()
        if mono_user and mono_user.last_synced_at.timestamp() < timezone.now().timestamp() - 3600 * 6:
            for balance in MonobankBalance.objects.filter(user=mono_user, watch=True):
                fetch_monobank_report(mono_user.token, balance.monobank_id, int(mono_user.last_synced_at.timestamp()),
                                      self.request.user, True)
            mono_user.save()

        return Balance.objects.filter(user=self.request.user)

    def perform_create(self, serializer):  # override to set user on balance creation
        if not serializer.validated_data.get('currency'):
            raise ValidationError({"currency": "Currency must be specified."})
        serializer.save(user=self.request.user)


class BalanceDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Balance.objects.all()
    permission_classes = [IsAuthenticated]

    serializer_class = BalanceSerializer

    def get_queryset(self):
        return Balance.objects.filter(user=self.request.user)


class BalanceSumm(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        balances = Balance.objects.filter(user=user)
        total_amount = sum(balance.amount * balance.currency.rate for balance in balances)
        return Response({'total_amount_uah': total_amount})


class ProcessFileUpload(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data['file']
            # try:
            balance_id = request.query_params.get('balance_id')
            balance = Balance.objects.get(pk=balance_id)
            if not balance or not (balance.user == request.user):
                raise Http404
            import_transaction_file(file, request.user, balance)
            return Response({'status': 'file processed successfully'})
            # except Exception as e:
            #    return Response({'error': str(e)}, status=400)
        return Response(serializer.errors, status=400)


class RefreshExchangeRates(APIView):

    def post(self, request):
        from finances.tasks import fetch_exchange_rates
        from finances.tasks import fetch_crypto_rates
        # fetch_exchange_rates()
        fetch_crypto_rates()
        return Response({'status': 'exchange rates refreshed successfully'})


class CurrencyList(generics.ListAPIView):
    serializer_class = CurrencySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Currency.objects.all()
        update = False

        try:
            uah = queryset.get(alpha_code='UAH')
            update = uah.updated.timestamp() < timezone.now().timestamp() - 3600
        except Currency.DoesNotExist:
            update = True

        if update:
            fetch_exchange_rates()
            fetch_crypto_rates()

        search = self.request.query_params.get('search')
        if search is not None:
            queryset = queryset.filter(alpha_code__icontains=search)
            if not queryset.exists() or queryset.count() == 0:
                queryset = Currency.objects.all()
                queryset = queryset.filter(name__icontains=search)
        return queryset


@api_view(['GET'])
def get_losses(request):
    queryset = Transaction.objects.filter(user=request.user, date__gt=timezone.now() - timedelta(days=31), amount__lt=0)
    total_losses = sum(transaction.amount * transaction.balance.currency.rate for transaction in queryset)
    return Response({"losses": total_losses})


@api_view(['GET'])
def get_profits(request):
    queryset = Transaction.objects.filter(user=request.user, date__gt=timezone.now() - timedelta(days=31), amount__gt=0)
    total_profits = sum(transaction.amount * transaction.balance.currency.rate for transaction in queryset)
    return Response({"profits": total_profits})
