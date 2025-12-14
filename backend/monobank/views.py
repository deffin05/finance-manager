from datetime import datetime, timedelta
from datetime import timezone as tz
from django.utils import timezone

import requests
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from finances.models import Currency, Balance
from monobank.models import MonobankUser, MonobankBalance, MonobankTransaction
from monobank.serializers import TokenSerializer, MonobankBalanceSerializer


# Create your views here.

def fetch_monobank_balances(token, user):
    url = "https://api.monobank.ua/personal/client-info"
    headers = {
        "Content-Type": "application/json",
        "X-Token": token,
    }

    response = requests.get(url, headers=headers)
    if response.ok:
        responseJson = response.json()

        for balance in responseJson["accounts"]:
            MonobankBalance.objects.get_or_create(
                monobank_id=balance["id"],
                defaults={
                    "amount": balance["balance"] / 100,
                    "name": balance["type"],
                    "currency": Currency.objects.get(num_code=balance["currencyCode"]),
                    "user": MonobankUser.objects.get(user=user),
                }
            )

        return True
    else:
        return False


def fetch_monobank_report(token, balance_id, timestamp, user):
    url = f"https://api.monobank.ua/personal/statement/{balance_id}/{timestamp}"
    headers = {
        "Content-Type": "application/json",
        "X-Token": token,
    }

    response = requests.get(url, headers=headers)
    print(response.status_code)
    if response.ok:
        response_json = response.json()

        for report in response_json:
            MonobankTransaction.objects.create(
                name=report["description"],
                category='-',
                monobank_id=report["id"],
                date=datetime.fromtimestamp(report["time"], tz=tz.utc),
                amount=report["amount"] / 100,
                balance=MonobankBalance.objects.get(monobank_id=balance_id).balance,
                user=user
            )


class TokenView(generics.CreateAPIView, generics.DestroyAPIView):
    serializer_class = TokenSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return get_object_or_404(MonobankUser, user=self.request.user)

    def perform_create(self, serializer):
        MonobankUser.objects.filter(user=self.request.user).delete()
        mono_user = serializer.save(user=self.request.user)

        valid = fetch_monobank_balances(mono_user.token, self.request.user)

        if not valid:
            MonobankUser.objects.filter(user=self.request.user).delete()
            raise ValidationError({"token": "Invalid token"})


class MonobankBalanceList(generics.ListAPIView):
    serializer_class = MonobankBalanceSerializer

    def get_queryset(self):
        queryset = MonobankBalance.objects.all().filter(user=MonobankUser.objects.get(user=self.request.user))
        return queryset


class MonobankBalanceWatch(generics.UpdateAPIView):
    serializer_class = MonobankBalanceSerializer

    def get_queryset(self):
        queryset = MonobankBalance.objects.all().filter(user=MonobankUser.objects.get(user=self.request.user))
        return queryset

    def perform_update(self, serializer):
        instance = serializer.save()

        print(instance.watch)
        if instance.watch:
            balance = Balance.objects.create(
                name=instance.name,
                user=self.request.user,
                amount=instance.amount,
                currency=instance.currency,
            )
            instance.balance = balance
            instance.save()

            timestamp = int((timezone.now() - timedelta(days=31)).timestamp())
            print(timestamp)
            fetch_monobank_report(MonobankUser.objects.get(user=self.request.user).token, instance.monobank_id,
                                  timestamp, self.request.user)
        else:
            instance.balance.delete()
            instance.balance = None
            instance.save()


@api_view(['GET'])
def verify_token(request):
    get_object_or_404(MonobankUser, user=request.user)
    return Response({"status": "OK"})
