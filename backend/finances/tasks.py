import pycountry
import requests

from finances.models import Currency


def fetch_exchange_rates():
    url = "https://api.monobank.ua/bank/currency"
    headers = {
        "Content-Type": "application/json",
    }

    currency_object = pycountry.currencies.get(numeric="980")
    Currency.objects.update_or_create(
        num_code=currency_object.numeric,
        alpha_code=currency_object.alpha_3,
        name=currency_object.name,
        rate=1,
    )

    response = requests.get(url, headers=headers)
    for rate in response.json():
        if rate["currencyCodeB"] != 980:
            continue
        code = rate["currencyCodeA"]
        currency_object = pycountry.currencies.get(numeric=str(code))

        if "rateCross" not in rate:
            rate["rateCross"] = rate["rateBuy"]

        Currency.objects.update_or_create(
            num_code=code,
            alpha_code=currency_object.alpha_3,
            name=currency_object.name,
            rate=rate["rateCross"],
        )
