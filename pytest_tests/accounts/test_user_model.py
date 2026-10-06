"""Тесты модели User.

Запуск:

    docker compose exec web pytest pytest_tests/accounts/test_user_model.py

Подробный вывод:

    docker compose exec web pytest pytest_tests/accounts/test_user_model.py -v

Один тест:

    docker compose exec web pytest pytest_tests/accounts/test_user_model.py::test_user_str_returns_username
"""

import pytest

from apps.accounts.models import User
from pytest_tests import constants as c


pytestmark = pytest.mark.model


def test_user_str_returns_username(user):
    """__str__ возвращает username."""
    assert str(user) == user.username


def test_user_default_role_is_fan(db):
    """Новый пользователь по умолчанию — болельщик."""
    new_user = User.objects.create_user(
        username='newbie',
        password=c.TEST_PASSWORD,
    )
    assert new_user.role == User.Role.FAN


def test_user_role_choices_display(coach_user):
    """get_role_display возвращает человекочитаемое имя."""
    assert coach_user.get_role_display() == 'Тренер'


def test_user_phone_and_avatar_optional(fan_user):
    """Телефон и аватар — необязательные поля."""
    assert fan_user.phone == ''
    assert not fan_user.avatar


def test_user_email_is_set(fan_user):
    """Email задаётся фабрикой."""
    assert '@' in fan_user.email
