import pytest
from finances.models import Transaction, Balance

@pytest.mark.django_db
def test_transaction_creates_balance_income(api_client, user):
    transaction_data = {
        'user': user.id,
        'amount': 100.00,
        'currency': 'USD',
    }
    api_client.force_authenticate(user=user)
    response = api_client.post("/transactions/", transaction_data, content_type="application/json")

    assert response.status_code == 201
    assert Transaction.objects.count() == 1
    assert Balance.objects.count() == 1
    balance = Balance.objects.get(user=user)
    assert balance.amount == 100.00
    assert balance.currency == 'USD'

@pytest.mark.django_db
def test_transaction_creates_balance_expense(api_client, user):
    Balance.objects.create(user=user, amount=500.00, currency="USD")
    transaction_data = {
        'user': user.id,
        'amount': -50.00,
        'currency': 'USD',
    }
    api_client.force_authenticate(user=user)
    response = api_client.post("/transactions/", transaction_data, content_type="application/json")

    assert response.status_code == 201
    assert Transaction.objects.count() == 1
    assert Balance.objects.count() == 1
    balance = Balance.objects.get(user=user)
    assert balance.amount == 450.00
    assert balance.currency == 'USD'

@pytest.mark.django_db
def test_transaction_creates_balance_independence(api_client, user):
    Balance.objects.create(user=user, amount=500.00, currency="USD")
    transaction_data = {
        'user': user.id,
        'amount': 100.00,
        'currency': 'EUR',
    }
    api_client.force_authenticate(user=user)
    response = api_client.post("/transactions/", transaction_data, content_type="application/json")

    assert response.status_code == 201
    assert Transaction.objects.count() == 1
    assert Balance.objects.count() == 2
    usd_balance = Balance.objects.get(user=user, currency="USD")
    assert usd_balance.amount == 500.00
    eur_balance = Balance.objects.get(user=user, currency="EUR")
    assert eur_balance.amount == 100.00