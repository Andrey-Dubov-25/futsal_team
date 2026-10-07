"""Smoke-тесты страниц авторизации.

Запуск:

    docker compose exec web pytest pytest_tests/web/test_auth_pages.py
"""

import pytest
from django.urls import reverse
from rest_framework import status

from apps.accounts.models import User
from pytest_tests import constants as c


pytestmark = pytest.mark.django_db


def test_login_page_returns_200(client):
    """Страница входа открывается."""
    response = client.get(reverse('web:login'))
    assert response.status_code == status.HTTP_200_OK


def test_register_page_returns_200(client):
    """Страница регистрации открывается."""
    response = client.get(reverse('web:register'))
    assert response.status_code == status.HTTP_200_OK


def test_profile_requires_login(client):
    """Профиль без логина — редирект."""
    response = client.get(reverse('web:profile'))
    assert response.status_code == status.HTTP_302_FOUND


def test_profile_shows_user_data(client, user):
    """Профиль показывает данные пользователя."""
    client.force_login(user)
    response = client.get(reverse('web:profile'))
    assert response.status_code == status.HTTP_200_OK
    assert user.username in response.content.decode()


def test_register_creates_user(client):
    """POST регистрации создаёт пользователя и логинит."""
    response = client.post(
        reverse('web:register'),
        {
            'username': 'newfan',
            'email': 'newfan@example.com',
            'first_name': 'Новый',
            'last_name': 'Болельщик',
            'password1': c.TEST_PASSWORD,
            'password2': c.TEST_PASSWORD,
        },
    )
    assert response.status_code == status.HTTP_302_FOUND

    new_user = User.objects.get(username='newfan')
    assert new_user.role == User.Role.FAN
    assert new_user.email == 'newfan@example.com'


def test_register_duplicate_username_fails(client, user):
    """Дублирующий username — форма с ошибкой."""
    response = client.post(
        reverse('web:register'),
        {
            'username': user.username,
            'password1': c.TEST_PASSWORD,
            'password2': c.TEST_PASSWORD,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.content.decode()
    assert 'уже существует' in content or 'already exists' in content


def test_register_password_mismatch_fails(client):
    """Несовпадающие пароли — форма с ошибкой."""
    response = client.post(
        reverse('web:register'),
        {
            'username': 'mismatch',
            'password1': c.TEST_PASSWORD,
            'password2': 'different',
        },
    )
    assert response.status_code == status.HTTP_200_OK


def test_login_with_valid_credentials(client, user):
    """Логин работает."""
    response = client.post(
        reverse('web:login'),
        {
            'username': user.username,
            'password': c.TEST_PASSWORD,
        },
    )
    assert response.status_code == status.HTTP_302_FOUND


def test_login_with_invalid_credentials(client, user):
    """Неверный пароль — форма с ошибкой."""
    response = client.post(
        reverse('web:login'),
        {
            'username': user.username,
            'password': 'wrong',
        },
    )
    assert response.status_code == status.HTTP_200_OK


def test_header_shows_login_for_anonymous(client):
    """В шапке для анонима — «Войти»."""
    response = client.get(reverse('web:home'))
    content = response.content.decode()
    assert 'Войти' in content


def test_header_shows_profile_for_authenticated(client, user):
    """В шапке для залогиненного — username."""
    client.force_login(user)
    response = client.get(reverse('web:home'))
    content = response.content.decode()
    assert user.username in content
