"""Smoke-тесты кастомных страниц ошибок.

Запуск:

    docker compose exec web pytest pytest_tests/web/test_error_pages.py
"""

import pytest
from django.urls import reverse
from rest_framework import status


pytestmark = pytest.mark.django_db


def test_404_page_returns_404(client):
    """Несуществующий URL возвращает 404 с кастомным шаблоном."""
    response = client.get('/this-page-does-not-exist-12345/')
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_404_page_shows_custom_content(client):
    """На 404-странице — кастомный текст и кнопка."""
    response = client.get('/this-page-does-not-exist-12345/')
    content = response.content.decode()

    assert '404' in content
    assert 'Страница не найдена' in content
    assert 'На главную' in content


def test_404_page_has_working_home_link(client):
    """Ссылка на главную работает."""
    response = client.get('/this-page-does-not-exist-12345/')
    content = response.content.decode()

    assert reverse('web:home') in content


def test_404_for_unknown_player(client):
    """Несуществующий игрок → 404 с кастомной страницей."""
    response = client.get('/players/99999/')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert 'Страница не найдена' in response.content.decode()


def test_404_for_unknown_match(client):
    """Несуществующий матч → 404."""
    response = client.get('/matches/99999/')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert 'Страница не найдена' in response.content.decode()


def test_404_for_unknown_news(client):
    """Несуществующая новость → 404."""
    response = client.get('/news/nonexistent-slug/')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert 'Страница не найдена' in response.content.decode()
