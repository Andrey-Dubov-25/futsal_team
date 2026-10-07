"""Smoke-тесты страниц игроков.

Запуск:

    docker compose exec web pytest pytest_tests/web/test_players_pages.py
"""

import pytest
from django.urls import reverse
from rest_framework import status


pytestmark = pytest.mark.django_db


def test_players_list_returns_200(client, sample_players):
    """Страница состава открывается."""
    response = client.get(reverse('web:players-list'))
    assert response.status_code == status.HTTP_200_OK


def test_players_list_shows_active_players(client, sample_players):
    """В списке отображаются активные игроки."""
    response = client.get(reverse('web:players-list'))
    content = response.content.decode()

    for player in sample_players:
        assert player.last_name in content
        assert player.first_name in content


def test_players_list_hides_inactive(client, db, sample_players):
    """Неактивные игроки не отображаются."""
    from pytest_tests.factories import PlayerFactory

    inactive = PlayerFactory(
        first_name='Неактивный',
        last_name='Игрок',
        is_active=False,
    )
    response = client.get(reverse('web:players-list'))
    content = response.content.decode()

    assert inactive.last_name not in content


def test_player_detail_returns_200(client, forward):
    """Детальная страница игрока открывается."""
    url = reverse('web:player-detail', args=[forward.pk])
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


def test_player_detail_shows_info(client, forward):
    """На детальной — имя, номер, позиция."""
    url = reverse('web:player-detail', args=[forward.pk])
    response = client.get(url)
    content = response.content.decode()

    assert forward.first_name in content
    assert forward.last_name in content
    assert forward.get_position_display() in content


def test_player_detail_404_for_unknown(client, db):
    """Несуществующий игрок — 404."""
    url = reverse('web:player-detail', args=[99999])
    response = client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_player_detail_404_for_inactive(client, db):
    """Неактивный игрок — 404."""
    from pytest_tests.factories import PlayerFactory

    inactive = PlayerFactory(is_active=False)
    url = reverse('web:player-detail', args=[inactive.pk])
    response = client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
