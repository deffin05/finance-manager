import pycountry
import requests
import os 
import json
import pandas as pd
import dotenv
from pathlib import Path

dotenv.load_dotenv()

from finances.models import Currency, Transaction, Balance

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
                id=currency_object.alpha_3,
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
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    for coin in response.json():
        id_val = coin["id"]
        alpha_code = coin["symbol"].upper()
        name = coin["name"]
        rate = coin["current_price"]

        Currency.objects.update_or_create(
            num_code=None,
            alpha_code=alpha_code,
            name=name,
            rate=rate,
            id=id_val
        )
    
COLUMN_MAPPING = {
    'date': [
        'Date', 'date', 'date_and_time',
        'Дата', 'дата', 'час_транзакції', 'дата_i_час_операції'
    ],
    'amount': [
        'card_currency_amount,_(uah)',
        'Amount', 'amount', 'amount_in_card_currency', 
        'Сума', 'сума', 'сума_в_валюті_картки', 'всього', 'сума_в_валюті_картки_(uah)'
    ],
    'description': [
        'Description', 'description', 
        'Опис', 'опис', 'призначення', 'деталі_операції', 'опис_операції'
    ],
    'category': [
        'Category', 'category',
        'Категорія', 'категорія', 'mcc', 'мсс'
    ],
    'balance': [
        'balance', 'баланс',
        'rest_at_the_end_of_the_period', 'залишок_після_операції', 'залишок_на_кінець_періоду'
    ]
}

CATEGORY_MAPPING = {
    '0742': [
        'Animals',
        'Тварини'
    ],
    '4111': [
        'Transport',
        'Транспорт'
    ],
    '4112': [
        'Train tickets',
        'Квитки на поїзд'
    ],
    '4814': [
        'Mobile top-up',
        'Поповнення мобільного'
    ],
    '4829': [
        'Transfers',
        'Перекази'
    ],
    '5211': [
        'Home and repair',
        'Дім та ремонт'
    ],
    '5297': [
        'Online stores',
        'Інтернет-магазини'
    ],
    '5411': [
        'Supermarkets and groceries',
        'Супермаркети та продукти'
    ],
    '5651': [
        'Clothes and shoes',
        'Одяг та взуття'
    ],
    '5812': [
        'Restaurants, cafes, bars',
        'Ресторани, кафе, бари'
    ],
    '5912': [
        'Pharmacies',
        'Аптеки'
    ],
    '5942': [
        'Books and stationery',
        'Книги та канцтовари'
    ],
    '6011': [
        'Cash withdrawal',
        'Зняття готівки'
    ],
    '6012': [
        'Loans',
        'Кредити'
    ],
    '6531': [
        'Payments by details',
        'Платежі за реквізитами'
    ],
    '6534': [
        'Enrollment',
        'Зарахування'
    ],
    '6538': [
        'Transfer crediting',
        'Зарахування переказу'
    ],
    '6539': [
        'Transfer from my card',
        'Зарахування зі своєї картки'
    ],
    '6540': [
        'Transfer to my card',
        'Переказ на свою картку'
    ],
    '6760': [
        'Savings',
        'Заощадження'
    ],
    '7299': [
        'Services',
        'Послуги'
    ],
    '8099': [
        'Medical services',
        'Медичні послуги'
    ],
    '8299': [
        'Education',
        'Освіта'
    ],
    '8398': [
        'Foundations and organizations',
        'Фонди та організації'
    ],
    '9999': [
        'Other',
        'Інше'
    ]
}

def normalize_headers(df):
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    for target_col, aliases in COLUMN_MAPPING.items():
        
        for alias in aliases:
            if alias in df.columns:
                df.rename(columns={alias: target_col}, inplace=True)
                break
    return df

NAME_TO_MCC = {
    alias: code 
    for code, aliases in CATEGORY_MAPPING.items() 
    for alias in aliases
}

def map_category(df):
    df['category'] = df['category'].replace(NAME_TO_MCC)
    df['category'] = df['category'].str.split('.').str[0]

current_dir = Path(__file__).parent 

# 2. Build the path to the JSON file relative to tasks.py
# This works regardless of where you run 'manage.py' from
file_path = current_dir / 'static' / 'mcc-en-groups.json'

with open(file_path, 'r', encoding='utf-8') as f:
    mcc_data = json.load(f)
MCC_GROUP_MAPPING = {
    item['mcc']: item['group']['description'] 
    for item in mcc_data
}

def normalize_category(df):
    df['category'] = df['category'].astype(str).str.split('.').str[0]
    df['category'] = df['category'].apply(lambda x: x.zfill(4) if x.isdigit() else x)
    df['category'] = df['category'].map(MCC_GROUP_MAPPING).fillna('Other')

def import_transaction_file(file_obj, user, balance):
    is_privatbank = False
    if file_obj.name.endswith('.csv'): #assume monobank csv
        df = pd.read_csv(file_obj)
    elif file_obj.name.endswith(('.xlsx')):
        # the first line is header info, so skip it
        df = pd.read_excel(file_obj, header=1)
        is_privatbank = True
    else:
        raise ValueError("Unsupported file type")
    df = normalize_headers(df)

    df['date'] = pd.to_datetime(df['date'], dayfirst=True)
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    df['balance'] = pd.to_numeric(df['balance'], errors='coerce')

    df.dropna(subset=['date', 'amount'], inplace=True)

    if is_privatbank: map_category(df)
    normalize_category(df)
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
    balance.save()
    
    return {"status": "success", "count": len(transactions)}
