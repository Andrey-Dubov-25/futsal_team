"""Тесты отображения ВК-новостей на сайте.

Запуск:

    docker compose exec web pytest pytest_tests/web/test_news_vk_pages.py
"""

import pytest
from django.urls import reverse

from pytest_tests.factories import NewsPostFactory


pytestmark = pytest.mark.django_db


def test_news_list_shows_vk_badge(client, db):
    """ВК-новость показывает бейдж ВК."""
    NewsPostFactory(
        title='ВК-новость',
        source='VK',
        external_id='-230450774_123',
        external_url='https://vk.com/wall-230450774_123',
    )

    response = client.get(reverse('web:news-list'))
    content = response.content.decode()

    assert 'ВК-новость' in content
    assert 'news-card__badge--vk' in content


def test_news_list_shows_video_badge(client, db):
    """Если has_video — бейдж с видео."""
    NewsPostFactory(
        title='Видео-новость',
        source='VK',
        external_id='-230450774_456',
        has_video=True,
    )

    response = client.get(reverse('web:news-list'))
    content = response.content.decode()

    assert 'news-card__badge--video' in content


def test_news_list_no_vk_badge_for_site_news(client, db):
    """Своя новость — без бейджа ВК."""
    NewsPostFactory(
        title='Своя новость',
        source='SITE',
    )

    response = client.get(reverse('web:news-list'))
    content = response.content.decode()

    assert 'Своя новость' in content
    assert 'news-card__badge--vk' not in content


def test_news_detail_shows_source(client, db):
    """На детальной — источник ВК."""
    news = NewsPostFactory(
        title='ВК-новость',
        source='VK',
        external_id='-230450774_789',
        external_url='https://vk.com/wall-230450774_789',
    )

    response = client.get(reverse('web:news-detail', args=[news.slug]))
    content = response.content.decode()

    assert 'ВКонтакте' in content
    assert 'vk.com/wall-230450774_789' in content


def test_news_detail_shows_video_button(client, db):
    """Видео — кнопка «Смотреть видео»."""
    news = NewsPostFactory(
        title='Видео',
        source='VK',
        external_id='-230450774_111',
        external_url='https://vk.com/wall-230450774_111',
        has_video=True,
    )

    response = client.get(reverse('web:news-detail', args=[news.slug]))
    content = response.content.decode()

    assert 'Смотреть видео' in content
