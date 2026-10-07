"""Smoke-тесты страниц матчей.

Запуск:

    docker compose exec web pytest pytest_tests/web/test_matches_pages.py
"""

import pytest
from django.urls import reverse
from rest_framework import status


pytestmark = pytest.mark.django_db


def test_matches_list_returns_200(client, finished_match):
    """Страница матчей открывается."""
    response = client.get(reverse('web:matches-list'))
    assert response.status_code == status.HTTP_200_OK


def test_matches_list_shows_upcoming(client, scheduled_match):
    """Будущий матч отображается в списке."""
    response = client.get(reverse('web:matches-list'))
    content = response.content.decode()
    assert scheduled_match.opponent in content


def test_matches_list_shows_finished(client, finished_match):
    """Завершённый матч отображается в списке."""
    response = client.get(reverse('web:matches-list'))
    content = response.content.decode()
    assert finished_match.opponent in content


def test_matches_list_shows_score_for_finished(client, finished_match):
    """Завершённый матч показывает счёт."""
    response = client.get(reverse('web:matches-list'))
    content = response.content.decode()
    score = f'{finished_match.our_score} : {finished_match.opponent_score}'
    assert score in content


def test_match_detail_returns_200(client, finished_match):
    """Детальная страница матча открывается."""
    url = reverse('web:match-detail', args=[finished_match.pk])
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


def test_match_detail_shows_opponent(client, finished_match):
    """На детальной — соперник и счёт."""
    url = reverse('web:match-detail', args=[finished_match.pk])
    response = client.get(url)
    content = response.content.decode()
    assert finished_match.opponent in content


def test_match_detail_shows_events(client, match_with_events):
    """На детальной — события матча."""
    url = reverse('web:match-detail', args=[match_with_events.pk])
    response = client.get(url)
    content = response.content.decode()
    assert 'Ход матча' in content


def test_match_detail_404_for_unknown(client, db):
    """Несуществующий матч — 404."""
    url = reverse('web:match-detail', args=[99999])
    response = client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_matches_list_empty_state(client, db):
    """Без матчей — показывается empty state."""
    response = client.get(reverse('web:matches-list'))
    content = response.content.decode()
    assert 'Ближайших матчей пока нет' in content
    assert 'Сыгранных матчей пока нет' in content
