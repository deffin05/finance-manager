from rest_framework import serializers

from finances.models import Transaction, Balance, Currency


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ['user', 'balance']


class BalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Balance
        fields = '__all__'
        read_only_fields = ['user']

    def get_amount(self, obj):
        # Convert to decimal, normalize removes trailing zeros
        # formatting ensures we don't get scientific notation (1E+2)
        value = obj.amount.normalize() 
        return "{:f}".format(value)
    
class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = '__all__'
