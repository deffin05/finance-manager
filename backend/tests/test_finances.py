import pytest
from rest_framework import status
from finances.models import Transaction, Balance, Currency
from django.contrib.auth.models import User
from decimal import Decimal

@pytest.mark.django_db
def test_transaction_increases_balance(api_client, user, balance):
    """
    Test that creating a positive transaction increases the linked balance.
    """
    transaction_data = {
        'name': 'Salary',
        'category': 'Income',
        'amount': 100.00
    }
    
    api_client.force_authenticate(user=user)
    response = api_client.post(f"/balance/{balance.id}/transactions/", transaction_data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert Transaction.objects.count() == 1
    
    balance.refresh_from_db()
    assert balance.amount == 100.00
    tx = Transaction.objects.first()
    assert tx.balance == balance

@pytest.mark.django_db
def test_transaction_decreases_balance(api_client, user, balance):
    """
    Test that creating a negative transaction (expense) decreases the balance.
    """
    balance.amount = 500.00
    balance.save()

    transaction_data = {
        'name': 'Groceries',
        'category': 'Food',
        'amount': -50.00,
    }

    api_client.force_authenticate(user=user)
    response = api_client.post(f"/balance/{balance.id}/transactions/", transaction_data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    
    balance.refresh_from_db()
    assert balance.amount == 450.00

@pytest.mark.django_db
def test_transaction_balance_independence(api_client, user, balance, eur_currency):
    """
    Test that a transaction on one balance does not affect another balance.
    """
    eur_balance = Balance.objects.create(
        user=user, 
        amount=500.00, 
        currency=eur_currency, 
        name="Travel Fund"
    )
    
    balance.amount = 1000.00
    balance.save()

    transaction_data = {
        'name': 'Souvenir',
        'category': 'Travel',
        'amount': -50.00,
    }

    api_client.force_authenticate(user=user)
    response = api_client.post(f"/balance/{eur_balance.id}/transactions/", transaction_data, format="json")

    assert response.status_code == status.HTTP_201_CREATED

    eur_balance.refresh_from_db()
    assert eur_balance.amount == 450.00

    balance.refresh_from_db()
    assert balance.amount == 1000.00

@pytest.mark.django_db
def test_cannot_use_other_users_balance(api_client, user, currency):
    """
    Test that a user cannot create a transaction linked to a balance they don't own.
    """
    other_user = User.objects.create_user(username='other', password='pw')
    other_balance = Balance.objects.create(
        user=other_user, 
        amount=100.00, 
        currency=currency, 
        name="Other's Cash"
    )

    transaction_data = {
        'name': 'Hack',
        'category': 'Theft',
        'amount': -100.00,
    }

    api_client.force_authenticate(user=user)
    response = api_client.post(f"/balance/{other_balance.id}/transactions/", transaction_data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "You do not own this balance" in str(response.data)

    other_balance.refresh_from_db()
    assert other_balance.amount == 100.00

@pytest.mark.django_db
def test_transaction_list_scope(api_client, user, balance):
    other_user = User.objects.create_user(username='otheruser', password='password123')
    other_balance = Balance.objects.create(user=other_user, amount=0, currency=balance.currency, name="O")
    
    Transaction.objects.create(user=user, balance=balance, amount=100.00, name="T1", category="C")
    Transaction.objects.create(user=other_user, balance=other_balance, amount=200.00, name="T2", category="C")

    api_client.force_authenticate(user=user)
    response = api_client.get(f"/balance/{balance.id}/transactions/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 1
    assert Decimal(response.data['results'][0]['amount']) == Decimal('100.00')

@pytest.mark.django_db
def test_balance_list_scope(api_client, user, currency):
    other_user = User.objects.create_user(username='otheruser', password='password123')
    
    Balance.objects.create(user=user, amount=300.00, currency=currency, name="Mine")
    Balance.objects.create(user=other_user, amount=400.00, currency=currency, name="Theirs")

    api_client.force_authenticate(user=user)
    response = api_client.get("/balance/")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert Decimal(response.data[0]['amount']) == Decimal('300.00')

@pytest.mark.django_db
def test_user_cannot_create_transaction_spoofing_user(api_client, user, balance):
    """
    Test that even if 'user' field is sent in payload, it is ignored/overridden
    by request.user in perform_create.
    """
    victim = User.objects.create_user(username="victim", password="password")
    
    payload = {
        "user": victim.id,
        "amount": "-100.00",
        "name": "Spoof",
        "category": "Test"
    }

    api_client.force_authenticate(user=user)
    api_client.post(f"/balance/{balance.id}/transactions/", payload, format="json")

    assert Transaction.objects.filter(user=victim).count() == 0
    
    assert Transaction.objects.filter(user=user).count() == 1

@pytest.mark.django_db
def test_list_balances_endpoint(api_client, user, currency):
    btc = Currency.objects.create(alpha_code="BTC", num_code=0, name="Bitcoin", id = "bitcoin", rate=50000)
    
    Balance.objects.create(user=user, amount=100.00, currency=currency, name="Fiat")
    Balance.objects.create(user=user, amount=0.5, currency=btc, name="Crypto")

    stranger = User.objects.create_user(username="stranger", password="6761")
    Balance.objects.create(user=stranger, amount=5000, currency=currency, name="Stranger")
    
    api_client.force_authenticate(user=user)
    response = api_client.get("/balance/")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2

    currencies = [item['currency'] for item in response.data]
    assert btc.id in currencies
    assert currency.id in currencies

@pytest.mark.django_db
def test_list_transactions_sorting(api_client, user, balance):
    Transaction.objects.create(user=user, balance=balance, amount=200.00, name="T1", category="C")
    Transaction.objects.create(user=user, balance=balance, amount=100.00, name="T2", category="C")
    Transaction.objects.create(user=user, balance=balance, amount=300.00, name="T3", category="C")

    api_client.force_authenticate(user=user)
    response = api_client.get(f"/balance/{balance.id}/transactions/?sort_by=amount&order=asc")

    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 3
    amounts = [float(item['amount']) for item in response.data['results']]
    assert amounts == [100.00, 200.00, 300.00]

@pytest.mark.django_db
def test_list_transactions_pagination(api_client, user, balance):
    for i in range(15):
        Transaction.objects.create(
            user=user, 
            balance=balance, 
            amount=10.00 * i, 
            name=f"Tx {i}", 
            category="Test"
        )

    api_client.force_authenticate(user=user)
    # Get page 2, size 5. Sorted by amount ASC implies:
    # Page 1: 0, 10, 20, 30, 40
    # Page 2: 50, 60, 70, 80, 90
    response = api_client.get(f"/balance/{balance.id}/transactions/?page=2&page_size=5&order=asc&sort_by=amount")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 5
    amounts = [float(item['amount']) for item in response.data['results']]
    assert amounts == [50.00, 60.00, 70.00, 80.00, 90.00]

@pytest.mark.django_db
def test_create_transaction_changes_balance(api_client, user, balance):
    """
    Test that creating a transaction updates the linked balance correctly.
    """
    initial_amount = balance.amount
    transaction_amount = Decimal(150.00)

    transaction_data = {
        'name': 'Freelance Work',
        'category': 'Income',
        'amount': transaction_amount,
    }

    api_client.force_authenticate(user=user)
    response = api_client.post(f"/balance/{balance.id}/transactions/", transaction_data, format="json")

    assert response.status_code == status.HTTP_201_CREATED

    balance.refresh_from_db()
    assert balance.amount == initial_amount + transaction_amount

@pytest.mark.django_db
def test_delete_transaction_updates_balance(api_client, user, balance):
    """
    Test that deleting a transaction updates the linked balance correctly.
    """
    transaction = Transaction.objects.create(
        name='Gift',
        category='Income',
        user=user,
        amount=Decimal(200.00),
        balance=balance
    )

    balance.amount += transaction.amount
    balance.save()

    initial_amount = balance.amount

    api_client.force_authenticate(user=user)
    response = api_client.delete(f"/transactions/{transaction.id}/")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    balance.refresh_from_db()
    assert balance.amount == initial_amount - transaction.amount


@pytest.mark.django_db
def test_update_transaction_changes_balance(api_client, user, balance):
    """
    Test that updating a transaction updates the linked balance correctly.
    """

    old_amount = Decimal("100.00") 
    
    transaction = Transaction.objects.create(
        name='Old Name',
        category='Old Category',
        user=user,
        amount=old_amount,
        balance=balance
    )

    balance.amount += old_amount
    balance.save()
    
    balance.refresh_from_db()
    initial_balance_amount = balance.amount

    new_amount_float = 250.00
    
    update_data = {
        'name': 'Updated Name',
        'category': 'Updated Category',
        'amount': new_amount_float,
        'balance': balance.id,
    }

    api_client.force_authenticate(user=user)
    response = api_client.put(f"/transactions/{transaction.id}/", update_data, format="json")

    assert response.status_code == status.HTTP_200_OK

    balance.refresh_from_db()
    
    new_amount = Decimal("250.00") 

    expected_amount = initial_balance_amount - old_amount + new_amount
    
    assert balance.amount == expected_amount

@pytest.mark.django_db
def test_get_balance_summation(api_client, user, currency):
    """
    Test that the BalanceSumm API returns the correct total amount in UAH.
    """
    uah_currency = currency
    eur_currency = Currency.objects.create(alpha_code="EUR", num_code=978, name="Euro", rate=40.00)

    Balance.objects.create(user=user, amount=100.00, currency=uah_currency, name="UAH Balance")
    Balance.objects.create(user=user, amount=5.00, currency=eur_currency, name="EUR Balance")

    api_client.force_authenticate(user=user)
    response = api_client.get("/balance/summ/")

    assert response.status_code == status.HTTP_200_OK

    expected_total = Decimal("100.00") + (Decimal("5.00") * Decimal("40.00"))
    
    assert Decimal(response.data['total_amount_uah']) == expected_total

@pytest.mark.django_db
def test_balance_summation_with_no_balances(api_client, user):
    """
    Test that the BalanceSumm API returns zero when the user has no balances.
    """
    api_client.force_authenticate(user=user)
    response = api_client.get("/balance/summ/")

    assert response.status_code == status.HTTP_200_OK
    assert Decimal(response.data['total_amount_uah']) == Decimal("0")

@pytest.mark.django_db
def test_balance_summation_with_crypto(api_client, user):
    """
    Test that the BalanceSumm API correctly sums balances including crypto currencies.
    """
    uah_currency = Currency.objects.create(alpha_code="UAH", num_code=980, name="Ukrainian Hryvnia", rate=1.0)
    btc_currency = Currency.objects.create(alpha_code="BTC", num_code=0, name="Bitcoin", rate=1000000.0)

    Balance.objects.create(user=user, amount=200.00, currency=uah_currency, name="UAH Balance")
    Balance.objects.create(user=user, amount=0.01, currency=btc_currency, name="BTC Balance")

    api_client.force_authenticate(user=user)
    response = api_client.get("/balance/summ/")

    assert response.status_code == status.HTTP_200_OK

    expected_total = Decimal("200.00") + (Decimal("0.01") * Decimal("1000000.0"))
    
    assert Decimal(response.data['total_amount_uah']) == expected_total