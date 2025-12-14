import pycountry
import requests
import os

from finances.models import Currency


def fetch_exchange_rates():
    url = "https://api.monobank.ua/bank/currency"
    headers = {
        "Content-Type": "application/json",
    }

    currency_object = pycountry.currencies.get(numeric="980")
    Currency.objects.update_or_create(
        num_code=currency_object.numeric,
        id=currency_object.alpha_3,
        name=currency_object.name,
        rate=1,
    )

    response = requests.get(url, headers=headers)
    for rate in response.json():
        if rate["currencyCodeB"] != 980:
            continue
        code = rate["currencyCodeA"]
        currency_object = pycountry.currencies.get(numeric=f"{code:03}")

        if "rateCross" not in rate:
            rate["rateCross"] = rate["rateBuy"]
        try:
            Currency.objects.update_or_create(
                num_code=code,
                alpha_code=currency_object.alpha_3,
                name=currency_object.name,
                defaults={
                    "rate":rate["rateCross"],
                }
            )
        except Exception as e:
            print(e)

def fetch_crypto_rates():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    headers = {
        "Content-Type": "application/json",
    }
    api_key = os.getenv("COINGECKO_API_KEY")
    if not api_key:
        raise ValueError("COINGECKO_API_KEY environment variable not set")
    params = {
        "vs_currency": "uah",
        "order": "market_cap_desc",
        "per_page": 250, #we get max 250 per page (and i dont care enough to implement pagination here yet, this would pollute our db with KirkCoins and such anyway)
        "page": 1,
        "sparkline": "false",
        "x_cg_demo_api_key": api_key #get your own API key from coingecko
    }

    #this actually fetches crypto to UAH rates directly, so no painful conversions needed
    currency_object = pycountry.currencies.get(numeric="980")
    Currency.objects.update_or_create(
        num_code=currency_object.numeric,
        alpha_code=currency_object.alpha_3,
        name=currency_object.name,
        rate=1,
    )
    response = requests.get(url, headers=headers)
    for coin in response.json():
        id = coin["id"]
        alpha_code = coin["symbol"].upper()
        name = coin["name"]
        rate = coin["current_price"]

        Currency.objects.update_or_create(
            num_code=None,
            alpha_code=alpha_code,
            name=name,
            rate=rate,
            id=id
        )
