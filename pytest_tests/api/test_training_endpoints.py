"""Тесты API тренировок.

Запуск:

    docker compose exec web pytest pytest_tests/api/test_training_endpoints.py
"""

import pytest
from rest_framework import status


pytestmark = pytest.mark.api


def test_list_trainings_returns_200(api_client, upcoming_training):
    """GET списка — 200."""
    response = api_client.get('/api/v1/trainings/')
    assert response.status_code == status.HTTP_200_OK


def test_upcoming_action(api_client, upcoming_training, past_training):
    """GET /upcoming/ возвращает только будущие."""
    response = api_client.get('/api/v1/trainings/upcoming/')
    assert response.status_code == status.HTTP_200_OK
    titles = [t['title'] for t in response.data]
    assert 'Будущая' in titles
    assert 'Прошедшая' not in titles


def test_upcoming_excludes_cancelled(
    api_client,
    upcoming_training,
    cancelled_training,
):
    """Отменённые не попадают в upcoming."""
    response = api_client.get('/api/v1/trainings/upcoming/')
    titles = [t['title'] for t in response.data]
    assert 'Отменённая' not in titles


def test_filter_trainings_by_is_cancelled(
    api_client,
    cancelled_training,
    upcoming_training,
):
    """?is_cancelled=true фильтрует."""
    response = api_client.get('/api/v1/trainings/?is_cancelled=true')
    assert response.status_code == status.HTTP_200_OK
    for item in response.data['results']:
        assert item['is_cancelled'] is True


def test_create_training_requires_auth(api_client):
    """POST без авторизации — 401."""
    response = api_client.post(
        '/api/v1/trainings/',
        {
            'title': 'X',
            'date': '2026-12-01T18:00:00Z',
            'location': 'Y',
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_training_with_auth(auth_client, head_coach):
    """POST с авторизацией — 201, coach привязан."""
    response = auth_client.post(
        '/api/v1/trainings/',
        {
            'title': 'Новая тренировка',
            'date': '2026-12-01T18:00:00Z',
            'location': 'Манеж',
            'coach_id': head_coach.id,
        },
        format='json',
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['coach']['id'] == head_coach.id
