"""Тесты пагинации.

Запуск:

    docker compose exec web pytest pytest_tests/web/test_pagination.py
"""

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from apps.matches.models import Match
from config import constants as c
from pytest_tests.factories import (
    AlbumFactory,
    FinishedMatchFactory,
    MatchFactory,
    NewsPostFactory,
)


pytestmark = pytest.mark.django_db


# --- Новости ---


def test_news_first_page_shows_first_batch(client, db):
    """На первой странице — ровно PAGE_SIZE_NEWS новостей."""
    for _ in range(c.PAGE_SIZE_NEWS + 5):
        NewsPostFactory()

    response = client.get(reverse('web:news-list'))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.context['news']) == c.PAGE_SIZE_NEWS


def test_news_second_page_shows_remaining(client, db):
    """На второй — остаток."""
    total = c.PAGE_SIZE_NEWS + 3
    for _ in range(total):
        NewsPostFactory()

    response = client.get(reverse('web:news-list') + '?page=2')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.context['news']) == 3


def test_news_shows_pagination_when_many(client, db):
    """При большом количестве — блок пагинации."""
    for _ in range(c.PAGE_SIZE_NEWS + 1):
        NewsPostFactory()

    response = client.get(reverse('web:news-list'))
    content = response.content.decode()
    assert 'pagination' in content
    assert 'Вперёд' in content


def test_news_hides_pagination_when_few(client, db):
    """При малом количестве — пагинация не показывается."""
    for _ in range(3):
        NewsPostFactory()

    response = client.get(reverse('web:news-list'))
    content = response.content.decode()
    assert 'pagination__link--arrow' not in content


def test_news_invalid_page_returns_last(client, db):
    """?page=999 — Django отдаёт последнюю страницу."""
    for _ in range(5):
        NewsPostFactory()

    response = client.get(reverse('web:news-list') + '?page=999')
    assert response.status_code == status.HTTP_200_OK


# --- Матчи ---


def test_matches_results_paginated(client, db):
    """Результаты матчей — постранично."""
    for _ in range(c.PAGE_SIZE_MATCHES + 2):
        FinishedMatchFactory()

    response = client.get(reverse('web:matches-list'))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.context['results']) == c.PAGE_SIZE_MATCHES


def test_matches_upcoming_not_paginated(client, db):
    """Ближайшие матчи — все на одной странице."""

    for _ in range(3):
        MatchFactory(
            status=Match.Status.SCHEDULED,
            date=timezone.now() + timedelta(days=7),
        )

    response = client.get(reverse('web:matches-list'))
    # upcoming — QuerySet, а не Page, значит все объекты
    assert len(response.context['upcoming']) == 3


# --- Галерея ---


def test_gallery_paginated(client, db):
    """Альбомы — постранично."""
    for _ in range(c.PAGE_SIZE_GALLERY + 3):
        AlbumFactory()

    response = client.get(reverse('web:gallery-list'))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.context['albums']) == c.PAGE_SIZE_GALLERY


def test_gallery_second_page(client, db):
    """Вторая страница — остаток."""
    for _ in range(c.PAGE_SIZE_GALLERY + 2):
        AlbumFactory()

    response = client.get(reverse('web:gallery-list') + '?page=2')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.context['albums']) == 2
