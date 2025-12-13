import pytest
from django.contrib.auth.models import User
from finances.models import Balance, Currency
from rest_framework.test import APIClient
from decimal import Decimal


@pytest.fixture
def api_client():
    yield APIClient()


@pytest.fixture
def user_data():
    yield {
        "username": "user",
        "email": "user@gmail.com",
        "password": "qwerty123",
    }


@pytest.fixture
def user(user_data):
    yield User.objects.create_user(**user_data)

@pytest.fixture
def currency():
    return Currency.objects.create(
        alpha_code="USD", 
        num_code=840, 
        name="US Dollar", 
        rate=1.0
    )

@pytest.fixture
def eur_currency():
    return Currency.objects.create(
        alpha_code="EUR", 
        num_code=978, 
        name="Euro", 
        rate=1.1
    )

@pytest.fixture
def balance(user, currency):
    return Balance.objects.create(
        user=user, 
        amount=Decimal(0.00), 
        currency=currency, 
        name="Main Wallet"
    )