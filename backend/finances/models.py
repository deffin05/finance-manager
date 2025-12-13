from django.contrib.auth.models import User
from django.db import models
from django.db.models.fields.related import ForeignKey
from django.utils import timezone


class Currency(models.Model):
    alpha_code = models.CharField(max_length=3, primary_key=True)
    num_code = models.IntegerField()
    name = models.CharField(max_length=100)
    rate = models.DecimalField(decimal_places=4, max_digits=20)  # Exchange rate to UAH
    updated = models.DateTimeField(auto_now=True)


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    amount = models.DecimalField(decimal_places=2, max_digits=20)


class Balance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=2, max_digits=20)
    currency = ForeignKey(Currency, on_delete=models.CASCADE)
