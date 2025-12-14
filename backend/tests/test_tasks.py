import pytest
from unittest.mock import patch, Mock
from decimal import Decimal
from finances.tasks import fetch_crypto_rates
from finances.models import Currency
import json

@pytest.mark.django_db
@patch('finances.tasks.requests.get')
@patch("finances.tasks.os.getenv")

def test_fetch_crypto_rates_with_file_data(mock_getenv, mock_requests_get):
    
    mock_getenv.return_value = "fake_key"

    with open("tests/coingecko_response.json", "r") as f:
        real_data = json.load(f)

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = real_data
    mock_requests_get.return_value = mock_response

    fetch_crypto_rates()

    for item in real_data:
        coin_id = item['id']
        json_price = item['current_price']
        
        db_coin = Currency.objects.get(id=coin_id)
        expected_price = Decimal(str(json_price))
        
        assert db_coin.rate == expected_price, \
            f"Price mismatch for {coin_id}: JSON had {expected_price}, DB has {db_coin.rate}"
            
        assert db_coin.name == item['name']
