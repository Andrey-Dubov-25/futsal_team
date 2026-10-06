"""Тесты API сотрудников.

Запуск:

    docker compose exec web pytest pytest_tests/api/test_staff_endpoints.py
"""

import pytest
from rest_framework import status


pytestmark = pytest.mark.api


def test_list_staff_returns_200(api_client, head_coach):
    """GET списка — 200."""
    response = api_client.get('/api/v1/staff/')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 1


def test_filter_staff_by_role(api_client, head_coach):
    """?role=HEAD_COACH фильтрует по должности."""
    response = api_client.get('/api/v1/staff/?role=HEAD_COACH')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 1


def test_staff_detail_has_full_name(api_client, head_coach):
    """GET детали — есть full_name и role_display."""
    response = api_client.get(f'/api/v1/staff/{head_coach.id}/')
    assert response.status_code == status.HTTP_200_OK
    assert 'full_name' in response.data
    assert 'role_display' in response.data


def test_create_staff_requires_auth(api_client):
    """POST без авторизации — 401."""
    response = api_client.post(
        '/api/v1/staff/',
        {'first_name': 'X', 'last_name': 'Y', 'role': 'HEAD_COACH'},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_staff_with_auth(auth_client):
    """POST с авторизацией — 201."""
    response = auth_client.post(
        '/api/v1/staff/',
        {
            'first_name': 'Новый',
            'last_name': 'Тренер',
            'role': 'ASSISTANT',
        },
        format='json',
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['first_name'] == 'Новый'
