"""Тесты API матчей.

Запуск:

    docker compose exec web pytest pytest_tests/api/test_matches_endpoints.py
"""

import pytest
from rest_framework import status

from apps.matches.models import Match
from pytest_tests import constants as c
from pytest_tests.factories import MatchFactory


pytestmark = pytest.mark.api


def test_list_matches_returns_200(api_client, finished_match):
    """GET списка матчей — 200."""
    response = api_client.get('/api/v1/matches/')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == c.TEST_MATCHES_TOTAL


def test_filter_matches_by_status(api_client, scheduled_match):
    """?status=SCH возвращает только запланированные."""
    response = api_client.get(
        f'/api/v1/matches/?status={Match.Status.SCHEDULED}',
    )
    assert response.status_code == status.HTTP_200_OK
    for match in response.data['results']:
        assert match['status'] == Match.Status.SCHEDULED


def test_filter_matches_by_is_home(api_client, db):
    """?is_home=true возвращает только домашние."""
    MatchFactory(is_home=True)
    MatchFactory(is_home=False)

    response = api_client.get('/api/v1/matches/?is_home=true')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 1


def test_upcoming_matches_action(api_client, db):
    """GET /upcoming/ возвращает будущие матчи."""
    MatchFactory(status=Match.Status.SCHEDULED)
    response = api_client.get('/api/v1/matches/upcoming/')
    assert response.status_code == status.HTTP_200_OK


def test_results_action_returns_finished(api_client, finished_match):
    """GET /results/ возвращает завершённые матчи."""
    response = api_client.get('/api/v1/matches/results/')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['status'] == Match.Status.FINISHED


def test_match_detail_includes_events(
    api_client,
    match_with_events,
    sample_players,
):
    """Детали матча содержат события."""
    response = api_client.get(
        f'/api/v1/matches/{match_with_events.id}/',
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['events']) == c.TEST_MATCH_EVENTS_COUNT


def test_create_match_requires_auth(api_client):
    """POST без авторизации — 401."""
    response = api_client.post(
        '/api/v1/matches/',
        {
            'opponent': 'X',
            'date': '2026-01-01T00:00:00Z',
            'location': 'Y',
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
