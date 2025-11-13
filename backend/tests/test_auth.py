import pytest
from django.contrib.auth.models import User


@pytest.mark.django_db
def test_create_user(api_client, user_data):
    response = api_client.post("/auth/users/", user_data, content_type="application/json")

    assert response.status_code == 201
    assert response.data['username'] == user_data['username']
    assert response.data['email'] == user_data['email']
    assert User.objects.count() == 1


@pytest.mark.django_db
def test_create_user_invalid_data(api_client):
    response = api_client.post("/auth/users/",
                               {'username': 'user', 'email': 'mail@gmail.com', 'password': '123'},
                               content_type="application/json")

    assert response.status_code == 400
    assert User.objects.count() == 0


@pytest.mark.django_db
def test_get_user(api_client, user):
    response = api_client.get(f"/auth/users/{user.id}/", content_type="application/json")

    assert response.status_code == 200
    assert response.data['username'] == user.username
    assert response.data['email'] == user.email
    assert not 'password' in response.data


@pytest.mark.django_db
def test_get_tokens(api_client, user):
    response = api_client.post("/auth/token/", {'username': 'user', 'password': 'qwerty123'},
                               content_type="application/json")

    assert response.status_code == 200
    assert len(response.data['access']) > 1
    assert len(response.data['access']) > 1


@pytest.mark.django_db
def test_get_token_invalid_user(api_client):
    response = api_client.post("/auth/token/", {'username': 'user', 'password': '123'}, content_type="application/json")

    assert response.status_code == 401
