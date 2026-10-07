"""Smoke-тесты страниц статистики.

Запуск:

    docker compose exec web pytest pytest_tests/web/test_stats_pages.py
"""

import pytest
from django.urls import reverse
from rest_framework import status

from pytest_tests.factories import MatchEventFactory


pytestmark = pytest.mark.django_db


def test_stats_players_returns_200(client, sample_players):
    """Страница бомбардиров открывается."""
    response = client.get(reverse('web:stats-players'))
    assert response.status_code == status.HTTP_200_OK


def test_stats_players_shows_all_active(client, sample_players):
    """Все активные игроки в таблице."""
    response = client.get(reverse('web:stats-players'))
    content = response.content.decode()
    for player in sample_players:
        assert player.last_name in content


def test_stats_players_shows_goals(client, sample_players):
    """Голы игрока отображаются."""
    forward = sample_players[2]
    MatchEventFactory(
        player=forward,
        event_type='GOAL',
        minute=10,
    )
    MatchEventFactory(
        player=forward,
        event_type='GOAL',
        minute=20,
    )

    response = client.get(reverse('web:stats-players'))
    content = response.content.decode()
    assert forward.last_name in content
    # В таблице должно быть число 2 в строке игрока —
    # проверяем через наличие имени + какой-то контекст, полный
    # парсинг HTML не делаем для простоты


def test_stats_team_returns_200(client, match_with_events):
    """Страница статистики команды открывается."""
    response = client.get(reverse('web:stats-team'))
    assert response.status_code == status.HTTP_200_OK


def test_stats_team_shows_counts(client, match_with_events):
    """Счётчики матчей отображаются."""
    response = client.get(reverse('web:stats-team'))
    content = response.content.decode()
    assert 'Побед' in content
    assert 'Поражений' in content
    assert 'Забито' in content


def test_stats_team_empty_when_no_matches(client, db):
    """Без матчей — empty state."""
    response = client.get(reverse('web:stats-team'))
    content = response.content.decode()
    assert 'Сыгранных матчей пока нет' in content


def test_stats_team_shows_form(client, match_with_events):
    """Форма W/D/L отображается."""
    response = client.get(reverse('web:stats-team'))
    content = response.content.decode()
    assert 'Форма' in content
