import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient


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