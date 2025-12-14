import requests
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from finances.models import Currency
from monobank.models import MonobankUser, MonobankBalance
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
                    "user": user
                }
            )

        return True
    else:
        return False


class TokenView(generics.CreateAPIView, generics.UpdateAPIView, generics.DestroyAPIView):
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
        queryset = MonobankBalance.objects.all().filter(user=self.request.user)
        return queryset


class MonobankBalanceWatch(generics.UpdateAPIView):
    serializer_class = MonobankBalanceSerializer
    def get_queryset(self):
        queryset = MonobankBalance.objects.all().filter(user=self.request.user)
        return queryset


@api_view(['GET'])
def verify_token(request):
    get_object_or_404(MonobankUser, user=request.user)
    return Response({"status": "OK"})
