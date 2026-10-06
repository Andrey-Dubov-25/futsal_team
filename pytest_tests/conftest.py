"""Глобальные фикстуры для всех тестов проекта."""

import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.matches.models import Match, MatchEvent
from apps.players.models import Player
from pytest_tests import constants as c
from pytest_tests.factories import (
    FinishedMatchFactory,
    MatchEventFactory,
    MatchFactory,
    NewsPostFactory,
    PlayerFactory,
    UserFactory,
)


# =============================================================================
# API-клиенты
# =============================================================================


@pytest.fixture
def api_client():
    """Анонимный API-клиент (без авторизации)."""
    return APIClient()


@pytest.fixture
def user(db):
    """Обычный пользователь с ролью FAN."""
    return UserFactory()


@pytest.fixture
def admin_user(db):
    """Суперпользователь с ролью ADMIN."""
    return UserFactory(
        username='admin',
        role=User.Role.ADMIN,
        is_staff=True,
        is_superuser=True,
    )


@pytest.fixture
def auth_client(api_client, user):
    """API-клиент с авторизацией обычного пользователя."""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    """API-клиент с авторизацией админа."""
    api_client.force_authenticate(user=admin_user)
    return api_client


# =============================================================================
# Пользователи (общие фикстуры для всех приложений)
# =============================================================================


@pytest.fixture
def fan_user(db):
    """Пользователь с ролью болельщик."""
    return UserFactory(
        username='fan1',
        role=User.Role.FAN,
    )


@pytest.fixture
def coach_user(db):
    """Пользователь с ролью тренер."""
    return UserFactory(
        username='coach1',
        role=User.Role.COACH,
    )


# =============================================================================
# Игроки
# =============================================================================


@pytest.fixture
def goalkeeper(db):
    """Игрок-вратарь."""
    return PlayerFactory(
        first_name='Иван',
        last_name='Вратарёв',
        number=1,
        position=Player.Position.GOALKEEPER,
    )


@pytest.fixture
def defender(db):
    """Игрок-защитник."""
    return PlayerFactory(
        first_name='Пётр',
        last_name='Защитников',
        number=7,
        position=Player.Position.DEFENDER,
    )


@pytest.fixture
def forward(db):
    """Игрок-нападающий."""
    return PlayerFactory(
        first_name='Сергей',
        last_name='Голеадоров',
        number=10,
        position=Player.Position.FORWARD,
    )


# =============================================================================
# Матчи
# =============================================================================


@pytest.fixture
def scheduled_match(db):
    """Запланированный матч без счёта."""
    return MatchFactory(
        status=Match.Status.SCHEDULED,
        our_score=None,
        opponent_score=None,
    )


@pytest.fixture
def finished_match(db):
    """Завершённый матч 3:1."""
    return FinishedMatchFactory()


@pytest.fixture
def goal_event(db, finished_match, forward):
    """Гол нападающего в завершённом матче."""
    return MatchEventFactory(
        match=finished_match,
        player=forward,
        event_type=MatchEvent.EventType.GOAL,
        minute=c.TEST_EVENT_MINUTE,
    )


# =============================================================================
# Новости
# =============================================================================


@pytest.fixture
def published_news(db):
    """Опубликованная новость."""
    author = UserFactory(username='author1')
    return NewsPostFactory(author=author, is_published=True)


@pytest.fixture
def draft_news(db):
    """Черновик новости."""
    author = UserFactory(username='author2')
    return NewsPostFactory(author=author, is_published=False)
