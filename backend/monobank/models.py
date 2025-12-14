from django.contrib.auth.models import User
from django.db import models

from finances.models import Balance, Currency


# Create your models here.

class MonobankUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    token = models.CharField(max_length=100)
    last_synced_at = models.DateTimeField(auto_now=True)


class MonobankBalance(models.Model):
    balance = models.OneToOneField(Balance, on_delete=models.SET_NULL, null=True, blank=True)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    user = models.ForeignKey(MonobankUser, on_delete=models.CASCADE)
    monobank_id = models.CharField(max_length=100)
    amount = models.DecimalField(decimal_places=10, max_digits=30)
    watch = models.BooleanField(default=False)
