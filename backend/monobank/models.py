from django.contrib.auth.models import User
from django.db import models

import finances.models


# Create your models here.

class MonobankUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    token = models.CharField(max_length=100)
    last_synced_at = models.DateTimeField()


class MonobankBalance(finances.models.Balance):
    monobank_id = models.CharField(max_length=100)
    watch = models.BooleanField(default=False)

