"""Тесты API новостей.

Запуск:

    docker compose exec web pytest pytest_tests/api/test_news_endpoints.py
"""

import pytest
from rest_framework import status


pytestmark = pytest.mark.api


def test_published_news_appears_in_list(api_client, published_news):
    """Опубликованная новость видна в списке."""
    response = api_client.get('/api/v1/news/')
    assert response.status_code == status.HTTP_200_OK
    slugs = [item['slug'] for item in response.data['results']]
    assert published_news.slug in slugs


def test_draft_news_not_in_list(api_client, draft_news):
    """Черновик не виден в списке."""
    response = api_client.get('/api/v1/news/')
    slugs = [item['slug'] for item in response.data['results']]
    assert draft_news.slug not in slugs


def test_news_detail_by_slug(api_client, published_news):
    """Новость открывается по slug."""
    response = api_client.get(
        f'/api/v1/news/{published_news.slug}/',
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data['title'] == published_news.title


def test_search_news_by_title(api_client, published_news):
    """?search= находит новость по заголовку."""
    word = published_news.title.split()[0]
    response = api_client.get(f'/api/v1/news/?search={word}')
    assert response.status_code == status.HTTP_200_OK


def test_create_news_requires_auth(api_client):
    """POST без авторизации — 401."""
    response = api_client.post(
        '/api/v1/news/',
        {'title': 'X', 'content': 'Y'},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
