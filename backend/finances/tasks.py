import pycountry
import requests
import os 
import pandas as pd

from finances.models import Currency, Transaction, Balance

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
    
COLUMN_MAPPING = {
    'date': [
        'Date', 'date', 'date_and_time',
        'Дата', 'дата', 'Час транзакції', 'дата_i_час_операції'
    ],
    'amount': [
        'card_currency_amount,_(uah)',
        'Amount', 'amount', 'amount_in_card_currency', 
        'Сума', 'сума', 'Сума у валюті картки', 'Всього', 'сума_в_валюті_картки_(uah)'
    ],
    'description': [
        'Description', 'description', 
        'Опис', 'опис', 'Призначення', 'деталі_операції'
    ],
    'category': [
        'Category', 'category',
        'Категорія', 'категорія', 'mcc', 'мсс'
    ],
    'balance': [
        'balance', 'баланс',
        'rest_at_the_end_of_the_period', 'категорія', 'mcc', 'мсс'
    ]
}

def normalize_headers(df):
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    for name, mapping in COLUMN_MAPPING.items:
        for i in name:
            if i in df.columns:
                df.rename(columns={i: mapping}, inplace=True)
                break
    return df

def import_transaction_file(file_obj, user, balance):
    if file_obj.name.endswith('.csv'): #assume monobank csv
        df = pd.read_csv(file_obj)
    elif file_obj.name.endswith(('.xls')):
        # the first line is header info, so skip it
        df = pd.read_excel(file_obj, header=1)
    else:
        raise ValueError("Unsupported file type")
    df = normalize_headers(df)

    df['date'] = pd.to_datetime(df['date'], dayfirst=True)
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    df['balance'] = pd.to_numeric(df['balance'], errors='coerce')

    df.dropna(subset=['date', 'amount'], inplace=True)

    transactions = []
    for _, row in df.iterrows():
        transactions.append(
            Transaction(
                date=row['date'],
                amount=row['amount'],
                # Use .get() in case description/category weren't in the file
                name=row.get('description', ''),
                category=row.get('category', 'Uncategorized'),
                user = user,
                balance = balance
            )
        )
    
    Transaction.objects.bulk_create(transactions)
    
    latest_balance = df.iloc[0]['balance']
    balance.amount = latest_balance

    return {"status": "success", "count": len(transactions)}
    


