"""Тесты JWT-авторизации.

Запуск:

    docker compose exec web pytest pytest_tests/api/test_auth.py
"""

import pytest
from rest_framework import status

from apps.players.models import Player
from pytest_tests import constants as c


pytestmark = pytest.mark.api


def test_login_with_valid_credentials(api_client, user):
    """Валидные креды возвращают access и refresh."""
    response = api_client.post(
        '/api/token/',
        {'username': user.username, 'password': c.TEST_PASSWORD},
        format='json',
    )
    assert response.status_code == status.HTTP_200_OK
    assert 'access' in response.data
    assert 'refresh' in response.data


def test_login_with_invalid_password(api_client, user):
    """Неверный пароль — 401."""
    response = api_client.post(
        '/api/token/',
        {'username': user.username, 'password': 'wrong'},
        format='json',
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_protected_endpoint_without_token(api_client):
    """POST без токена — 401."""
    response = api_client.post(
        '/api/v1/players/',
        {
            'first_name': 'X',
            'last_name': 'Y',
            'position': Player.Position.FORWARD,
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_protected_endpoint_with_token(auth_client):
    """POST с авторизацией — 201."""
    response = auth_client.post(
        '/api/v1/players/',
        {
            'first_name': 'Тест',
            'last_name': 'Тестов',
            'position': Player.Position.FORWARD,
        },
        format='json',
    )
    assert response.status_code == status.HTTP_201_CREATED


def test_refresh_token(api_client, user):
    """Refresh-токен обменивается на новый access."""
    login = api_client.post(
        '/api/token/',
        {'username': user.username, 'password': c.TEST_PASSWORD},
        format='json',
    )
    response = api_client.post(
        '/api/token/refresh/',
        {'refresh': login.data['refresh']},
        format='json',
    )
    assert response.status_code == status.HTTP_200_OK
    assert 'access' in response.data
