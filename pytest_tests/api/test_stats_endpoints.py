"""Тесты эндпоинтов статистики.

Запуск:

    docker compose exec web pytest pytest_tests/api/test_stats_endpoints.py
"""

import pytest
from rest_framework import status

from apps.players.models import Player
from pytest_tests import constants as c


pytestmark = pytest.mark.api


def test_player_stats_endpoint_returns_200(api_client, match_with_events):
    """GET /api/v1/stats/players/ — 200."""
    response = api_client.get('/api/v1/stats/players/')
    assert response.status_code == status.HTTP_200_OK


def test_player_stats_counts_goals(api_client, match_with_events):
    """Нападающий с двумя голами — 2 в графе goals."""
    response = api_client.get('/api/v1/stats/players/')
    forward_stats = next(
        p for p in response.data if p['position'] == Player.Position.FORWARD
    )
    assert forward_stats['goals'] == c.TEST_GOALS_FORWARD
    assert forward_stats['points'] == c.TEST_GOALS_FORWARD


def test_player_stats_counts_assists(api_client, match_with_events):
    """Защитник с одной передачей — 1 в графе assists."""
    response = api_client.get('/api/v1/stats/players/')
    defender_stats = next(
        p for p in response.data if p['position'] == Player.Position.DEFENDER
    )
    assert defender_stats['assists'] == c.TEST_ASSISTS_DEFENDER
    assert defender_stats['points'] == c.TEST_ASSISTS_DEFENDER


def test_player_stats_includes_all_active_players(
    api_client,
    match_with_events,
):
    """Все активные игроки в статистике, даже без событий."""
    response = api_client.get('/api/v1/stats/players/')
    assert len(response.data) == c.TEST_TOTAL_PLAYERS


def test_team_stats_endpoint_returns_200(api_client, match_with_events):
    """GET /api/v1/stats/team/ — 200."""
    response = api_client.get('/api/v1/stats/team/')
    assert response.status_code == status.HTTP_200_OK


def test_team_stats_aggregates_correctly(api_client, match_with_events):
    """Сводка команды считает победы, голы и форму."""
    response = api_client.get('/api/v1/stats/team/')
    assert response.data['matches_total'] == c.TEST_MATCHES_TOTAL
    assert response.data['matches_won'] == c.TEST_MATCHES_TOTAL
    assert response.data['matches_drawn'] == 0
    assert response.data['matches_lost'] == 0
    assert response.data['goals_scored'] == c.TEST_GOALS_SCORED
    assert response.data['goals_conceded'] == c.TEST_GOALS_CONCEDED
    assert response.data['goal_difference'] == c.TEST_GOAL_DIFFERENCE
    assert response.data['form'] == ['W']


def test_team_stats_empty_when_no_matches(api_client, db):
    """Без матчей статистика — нули и пустая форма."""
    response = api_client.get('/api/v1/stats/team/')
    assert response.data['matches_total'] == 0
    assert response.data['goals_scored'] == 0
    assert response.data['form'] == []


def test_team_stats_win_rate(api_client, match_with_events):
    """Win rate — процент побед."""
    response = api_client.get('/api/v1/stats/team/')
    assert response.data['win_rate'] == c.TEST_WIN_RATE


def test_player_stats_publicly_accessible(api_client, match_with_events):
    """Статистика игроков доступна без авторизации."""
    response = api_client.get('/api/v1/stats/players/')
    assert response.status_code == status.HTTP_200_OK


def test_team_stats_publicly_accessible(api_client, match_with_events):
    """Статистика команды доступна без авторизации."""
    response = api_client.get('/api/v1/stats/team/')
    assert response.status_code == status.HTTP_200_OK
