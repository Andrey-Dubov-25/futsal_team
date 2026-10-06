"""Тесты API игроков.

Запуск:

    docker compose exec web pytest pytest_tests/api/test_players_endpoints.py
"""

import pytest
from rest_framework import status

from apps.players.models import Player
from pytest_tests import constants as c


pytestmark = pytest.mark.api


def test_list_players_returns_200(api_client, sample_players):
    """GET списка игроков — 200, все игроки в результатах."""
    response = api_client.get('/api/v1/players/')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == c.TEST_TOTAL_PLAYERS


def test_filter_players_by_position(api_client, sample_players):
    """?position=GK возвращает только вратарей."""
    response = api_client.get(
        f'/api/v1/players/?position={Player.Position.GOALKEEPER}',
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 1
    assert (
        response.data['results'][0]['position'] == Player.Position.GOALKEEPER
    )


def test_filter_players_by_is_active(api_client, sample_players):
    """?is_active=true возвращает только активных."""
    response = api_client.get('/api/v1/players/?is_active=true')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == c.TEST_TOTAL_PLAYERS


def test_search_players_by_last_name(api_client, sample_players):
    """?search=Голеадоров находит нападающего."""
    response = api_client.get('/api/v1/players/?search=Голеадоров')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 1


def test_order_players_by_number_desc(api_client, sample_players):
    """?ordering=-number сортирует по убыванию номера."""
    response = api_client.get('/api/v1/players/?ordering=-number')
    numbers = [p['number'] for p in response.data['results']]
    assert numbers == sorted(numbers, reverse=True)


def test_player_detail(api_client, forward):
    """GET детали игрока — 200, есть full_name."""
    response = api_client.get(f'/api/v1/players/{forward.id}/')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['number'] == forward.number
    assert 'full_name' in response.data


def test_create_player_requires_auth(api_client):
    """POST без авторизации — 401."""
    response = api_client.post(
        '/api/v1/players/',
        {
            'first_name': 'X',
            'last_name': 'Y',
            'position': Player.Position.FORWARD,
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_player_with_auth(auth_client):
    """POST с авторизацией — 201, игрок создан."""
    response = auth_client.post(
        '/api/v1/players/',
        {
            'first_name': 'Новый',
            'last_name': 'Игрок',
            'position': Player.Position.FORWARD,
            'number': c.TEST_DEFAULT_NUMBER,
        },
        format='json',
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['first_name'] == 'Новый'


def test_update_player_requires_auth(api_client, forward):
    """PATCH без авторизации — 401."""
    response = api_client.patch(
        f'/api/v1/players/{forward.id}/',
        {'first_name': 'Изменённый'},
        format='json',
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_delete_player_requires_auth(api_client, forward):
    """DELETE без авторизации — 401."""
    response = api_client.delete(f'/api/v1/players/{forward.id}/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
