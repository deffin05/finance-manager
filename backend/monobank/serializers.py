from rest_framework import serializers

from monobank.models import MonobankUser


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonobankUser
        fields = ['user', 'token']
        readonly_fields = ['user']