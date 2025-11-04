from django.contrib.auth.models import User
from django.db import models

# Create your models here.

CURRENCIES = {
    "EUR": "Euro",
    "USD": "US Dollar",
    "UAH": "Ukrainian hryvnia",
    "BTC": "Bitcoin",
}
class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    amount = models.DecimalField(decimal_places=2, max_digits=20)
    currency = models.CharField(max_length=3, choices=CURRENCIES.items())

class Balance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=2, max_digits=20)
    currency = models.CharField(max_length=3, choices=CURRENCIES.items())