"""Smoke-тесты SEO-элементов.

Запуск:

    docker compose exec web pytest pytest_tests/web/test_seo.py
"""

import pytest
from django.urls import reverse
from rest_framework import status


pytestmark = pytest.mark.django_db


def test_robots_txt_returns_200(client):
    """robots.txt доступен."""
    response = client.get('/robots.txt')
    assert response.status_code == status.HTTP_200_OK
    assert response['Content-Type'].startswith('text/plain')


def test_robots_txt_blocks_admin_and_api(client):
    """robots.txt закрывает /admin/ и /api/."""
    response = client.get('/robots.txt')
    content = response.content.decode()

    assert 'Disallow: /admin/' in content
    assert 'Disallow: /api/' in content


def test_robots_txt_links_sitemap(client):
    """robots.txt содержит ссылку на sitemap."""
    response = client.get('/robots.txt')
    content = response.content.decode()

    assert 'Sitemap:' in content
    assert '/sitemap.xml' in content


def test_sitemap_returns_200(client):
    """sitemap.xml доступен."""
    response = client.get('/sitemap.xml')
    assert response.status_code == status.HTTP_200_OK
    assert response['Content-Type'].startswith('application/xml')


def test_sitemap_contains_main_urls(client):
    """sitemap.xml содержит основные URL."""
    response = client.get('/sitemap.xml')
    content = response.content.decode()

    assert '<urlset' in content
    assert '/players/' in content
    assert '/matches/' in content
    assert '/news/' in content


def test_sitemap_includes_news(client, published_news):
    """sitemap.xml содержит URL опубликованной новости."""
    response = client.get('/sitemap.xml')
    content = response.content.decode()
    assert published_news.slug in content


def test_sitemap_excludes_drafts(client, draft_news):
    """sitemap.xml не содержит черновики."""
    response = client.get('/sitemap.xml')
    content = response.content.decode()
    assert draft_news.slug not in content


def test_sitemap_includes_albums(client, album):
    """sitemap.xml содержит URL альбома."""
    response = client.get('/sitemap.xml')
    content = response.content.decode()
    assert album.slug in content


def test_home_has_description_meta(client):
    """Главная содержит meta description."""
    response = client.get(reverse('web:home'))
    content = response.content.decode()

    assert '<meta name="description"' in content


def test_home_has_og_tags(client):
    """Главная содержит Open Graph."""
    response = client.get(reverse('web:home'))
    content = response.content.decode()

    assert 'og:title' in content
    assert 'og:description' in content
    assert 'og:type' in content


def test_news_detail_uses_og_article(client, published_news):
    """Детальная новости — og:type=article."""
    url = reverse('web:news-detail', args=[published_news.slug])
    response = client.get(url)
    content = response.content.decode()

    assert 'og:type' in content
    assert 'article' in content


def test_page_has_canonical_link(client):
    """Страницы содержат canonical."""
    response = client.get(reverse('web:home'))
    content = response.content.decode()

    assert 'rel="canonical"' in content
