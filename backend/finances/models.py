from django.contrib.auth.models import User
from django.db import models
from django.db.models.fields.related import ForeignKey
from django.utils import timezone


class Currency(models.Model):
    id = models.CharField(max_length=100, primary_key=True, blank=True)
    alpha_code = models.CharField(max_length=20, blank=True)    
    num_code = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=100)
    rate = models.DecimalField(decimal_places=10, max_digits=30)  # Exchange rate to UAH
    updated = models.DateTimeField(auto_now=True)
    def save(self, *args, **kwargs):
        if not self.alpha_code:
            self.alpha_code = str(self.id).upper()
        if not self.id:
            self.id = str(self.alpha_code).lower()
        super().save(*args, **kwargs)


class Transaction(models.Model):
    name = models.CharField(max_length=200, blank=True, default="")
    category = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    amount = models.DecimalField(decimal_places=10, max_digits=30)
    balance = models.ForeignKey('Balance', on_delete=models.CASCADE)


class Balance(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=10, max_digits=30)
    currency = ForeignKey(Currency, on_delete=models.CASCADE)
