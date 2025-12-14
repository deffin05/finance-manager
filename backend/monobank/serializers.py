from rest_framework import serializers

from finances.models import Transaction
from monobank.models import MonobankUser, MonobankBalance, MonobankTransaction


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonobankUser
        fields = ['user', 'token']
        read_only_fields = ['user']


class MonobankBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonobankBalance
        fields = '__all__'


class MonobankTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonobankTransaction
        fields = '__all__'

    def create(self, validated_data):
        monobank_id = validated_data['monobank_id']

        if monobank_id:
            try:
                return MonobankTransaction.objects.get(monobank_id=monobank_id)
            except MonobankTransaction.DoesNotExist:
                pass

        date = validated_data['date']
        amount = validated_data['amount']
        currency = validated_data['currency']

        transaction = Transaction.objects.filter(date=date, amount=amount, currency=currency).first()

        if transaction:
            return transaction

        return super().create(validated_data)
