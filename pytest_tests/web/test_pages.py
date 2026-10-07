"""Smoke-тесты HTML-страниц.

Запуск:

    docker compose exec web pytest pytest_tests/web/test_pages.py
"""

import pytest
from django.urls import reverse


pytestmark = pytest.mark.django_db


def test_homepage_returns_200(client):
    """Главная страница открывается."""
    response = client.get(reverse('web:home'))
    assert response.status_code == 200


def test_homepage_uses_base_template(client):
    """Страница использует базовый шаблон."""
    response = client.get(reverse('web:home'))
    assert b'<!DOCTYPE html>' in response.content
    assert 'Мини-футбольная команда'.encode() in response.content


def test_homepage_contains_header_and_footer(client):
    """На странице есть header и footer."""
    response = client.get(reverse('web:home'))
    content = response.content
    assert b'header' in content
    assert b'footer' in content
