"""Тесты JWT-авторизации.

Запуск:

    docker compose exec web pytest pytest_tests/api/test_auth.py
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status

from apps.players.models import Player
from pytest_tests import constants as c


User = get_user_model()

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


def test_register_new_user(db, api_client):
    """POST /auth/register/ создаёт пользователя и возвращает токены."""
    response = api_client.post(
        '/api/v1/auth/register/',
        {
            'username': 'newfan',
            'email': 'newfan@example.com',
            'first_name': 'Новый',
            'last_name': 'Болельщик',
            'password': c.TEST_PASSWORD,
            'password_confirm': c.TEST_PASSWORD,
        },
        format='json',
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert 'access' in response.data
    assert 'refresh' in response.data
    assert response.data['user']['username'] == 'newfan'
    assert response.data['user']['role'] == User.Role.FAN


def test_register_duplicate_username(api_client, user):
    """Повторный username — 400."""
    response = api_client.post(
        '/api/v1/auth/register/',
        {
            'username': user.username,
            'password': c.TEST_PASSWORD,
            'password_confirm': c.TEST_PASSWORD,
        },
        format='json',
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'username' in response.data


def test_register_password_mismatch(db, api_client):
    """Несовпадающие пароли — 400."""
    response = api_client.post(
        '/api/v1/auth/register/',
        {
            'username': 'mismatch',
            'password': c.TEST_PASSWORD,
            'password_confirm': 'different',
        },
        format='json',
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'password_confirm' in response.data


def test_me_requires_auth(api_client):
    """GET /auth/me/ без токена — 401."""
    response = api_client.get('/api/v1/auth/me/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_me_returns_current_user(auth_client, user):
    """GET /auth/me/ возвращает профиль залогиненного."""
    response = auth_client.get('/api/v1/auth/me/')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['username'] == user.username
    assert 'role_display' in response.data


def test_me_update_profile(auth_client, user):
    """PATCH /auth/me/ обновляет профиль."""
    response = auth_client.patch(
        '/api/v1/auth/me/',
        {
            'first_name': 'Обновлённый',
            'phone': '+79990001122',
        },
        format='json',
    )
    assert response.status_code == status.HTTP_200_OK
    user.refresh_from_db()
    assert user.first_name == 'Обновлённый'
    assert user.phone == '+79990001122'


def test_logout_revokes_token(api_client, user):
    """POST /auth/logout/ отзывает refresh-токен."""
    login = api_client.post(
        '/api/token/',
        {'username': user.username, 'password': c.TEST_PASSWORD},
        format='json',
    )
    refresh = login.data['refresh']

    # Логинимся как этот юзер
    api_client.force_authenticate(user=user)
    response = api_client.post(
        '/api/v1/auth/logout/',
        {'refresh': refresh},
        format='json',
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_logout_without_refresh(api_client, user):
    """POST /auth/logout/ без refresh — 400."""
    api_client.force_authenticate(user=user)
    response = api_client.post('/api/v1/auth/logout/', {}, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
