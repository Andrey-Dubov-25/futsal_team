"""Глобальные фикстуры для всех тестов проекта."""

from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.matches.models import Match, MatchEvent
from apps.players.models import Player
from apps.staff.models import Staff
from pytest_tests import constants as c
from pytest_tests.factories import (
    AlbumFactory,
    CommentFactory,
    FinishedMatchFactory,
    MatchEventFactory,
    MatchFactory,
    NewsPostFactory,
    PhotoFactory,
    PlayerFactory,
    StaffFactory,
    TrainingFactory,
    UserFactory,
)


@pytest.fixture(autouse=True)
def use_tmp_media_root(settings, tmp_path):
    """Перенаправить MEDIA_ROOT в tmp_path для всех тестов.

    Это гарантирует, что тестовые файлы не попадут в реальный
    media/, а будут лежать во временной папке pytest.
    """
    settings.MEDIA_ROOT = tmp_path


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


@pytest.fixture
def sample_players(db):
    """Набор из трёх игроков разных позиций."""
    return [
        PlayerFactory(
            first_name='Иван',
            last_name='Вратарёв',
            number=1,
            position=Player.Position.GOALKEEPER,
        ),
        PlayerFactory(
            first_name='Пётр',
            last_name='Защитников',
            number=7,
            position=Player.Position.DEFENDER,
        ),
        PlayerFactory(
            first_name='Сергей',
            last_name='Голеадоров',
            number=10,
            position=Player.Position.FORWARD,
        ),
    ]


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


# =============================================================================
# Комментарии
# =============================================================================


@pytest.fixture
def comment_on_news(db, published_news, user):
    """Комментарий пользователя к опубликованной новости."""

    return CommentFactory(
        post=published_news,
        author=user,
        text='Отличная победа!',
    )


@pytest.fixture
def another_user(db):
    """Второй пользователь для тестов прав доступа."""
    return UserFactory(username='another1')


# =============================================================================
# Staff
# =============================================================================


@pytest.fixture
def head_coach(db):
    """Главный тренер."""

    return StaffFactory(
        first_name='Виктор',
        last_name='Победоносцев',
        role=Staff.Role.HEAD_COACH,
        order=1,
    )


@pytest.fixture
def assistant_coach(db):
    """Ассистент."""

    return StaffFactory(
        first_name='Андрей',
        last_name='Помощников',
        role=Staff.Role.ASSISTANT,
        order=2,
    )


# =============================================================================
# Training
# =============================================================================


@pytest.fixture
def past_training(db, head_coach):
    """Прошедшая тренировка."""

    return TrainingFactory(
        title='Прошедшая',
        date=timezone.now() - timedelta(days=7),
        coach=head_coach,
    )


@pytest.fixture
def upcoming_training(db, head_coach):
    """Будущая тренировка."""

    return TrainingFactory(
        title='Будущая',
        date=timezone.now() + timedelta(days=1),
        coach=head_coach,
    )


@pytest.fixture
def cancelled_training(db, head_coach):
    """Отменённая тренировка."""

    return TrainingFactory(
        title='Отменённая',
        date=timezone.now() + timedelta(days=2),
        coach=head_coach,
        is_cancelled=True,
    )


# =============================================================================
# Gallery
# =============================================================================


@pytest.fixture
def album(db):
    """Опубликованный альбом."""
    return AlbumFactory(title='Матч с Динамо')


@pytest.fixture
def photo_in_album(db, album):
    """Фотография в альбоме."""
    return PhotoFactory(album=album, caption='Победный гол')
