# Finance manager

## Description

This is a web app for tracking personal finances. It allows you to view
your savings from different sources, such as stocks, cryptocurrencies
and other currencies. It will be displayed in an overall dashboard 
with a graph to see your profits or losses over time. We plan to support
integrations with Monobank and probably other financial institutions.


## Features
- Authentication
  - Sign-up and sign-in
  - Hashed, salted, peppered passwords database
  - JWT Authentication
  - monobank API token integration
- API Integration
  - monobank API integration for currency conversion and user spending
  - Binance API
  - Stock price APIs?
  - useless LLM integration to "make up" for the lack of other bank APIs?
- Interactive graphs for total net worth, net worth by source, spending by category

## Team
- Dmytro Melnyk
- Konstantin Sadykov

## Set-up

### Set environment variables in .env
```
DJANGO_SECRET_KEY="YOUR_KEY"
COINGECKO_API_KEY = "YOUR_API_KEY"
```

### Install dependencies
```bash
pip install requirements.txt
```

### Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Run server
```bash
python manage.py runserver
```