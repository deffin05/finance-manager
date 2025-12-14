from rest_framework import serializers

from monobank.models import MonobankUser, MonobankBalance


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonobankUser
        fields = ['user', 'token']
        read_only_fields = ['user']

class MonobankBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonobankBalance
        fields = '__all__'