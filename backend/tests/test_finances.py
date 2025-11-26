import pytest
from finances.models import Transaction, Balance
from django.contrib.auth.models import User # we need User model for creating test users to test scope restriction

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

@pytest.mark.django_db
def test_transaction_list_scope(api_client, user):
    other_user = User.objects.create_user(username='otheruser', password='password123')
    Transaction.objects.create(user=user, amount=100.00, currency="USD")
    Transaction.objects.create(user=other_user, amount=200.00, currency="USD")

    api_client.force_authenticate(user=user)
    response = api_client.get("/transactions/", content_type="application/json")

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['amount'] == '100.00'

@pytest.mark.django_db
def test_balance_list_scope(api_client, user):
    other_user = User.objects.create_user(username='otheruser', password='password123')
    Balance.objects.create(user=user, amount=300.00, currency="USD")
    Balance.objects.create(user=other_user, amount=400.00, currency="USD")

    api_client.force_authenticate(user=user)
    response = api_client.get("/balance/", content_type="application/json")

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['amount'] == '300.00'

@pytest.mark.django_db
def test_user_cannot_create_transaction_for_others(api_client, user):
    victim = User.objects.create_user(username="victim", password="password")

    payload = { # Request payload spoofing the victim user id
        "user": victim.id, 
        "amount": "-100.00",
        "currency": "USD"
    }

    api_client.force_authenticate(user=user)
    api_client.post("/transactions/", payload)

    #The victim should have 0 transactions
    assert Transaction.objects.filter(user=victim).count() == 0
    
    #The attacker (user) should have 1 transaction
    assert Transaction.objects.filter(user=user).count() == 1

@pytest.mark.django_db
def test_list_balances_endpoint(api_client, user):
    Balance.objects.create(user=user, amount = 100.00, currency = "USD")
    Balance.objects.create(user=user, amount=0.5, currency="BTC")

    stranger = User.objects.create_user(username="stranger", password="6761")
    Balance.objects.create(user=stranger, amount=5000, currency="EUR")
    api_client.force_authenticate(user=user)
    response = api_client.get("/balance/")

    assert response.status_code == 200
    assert len(response.data) == 2
    currencies = [item['currency'] for item in response.data]
    assert "USD" in currencies
    assert "BTC" in currencies
    assert "EUR" not in currencies