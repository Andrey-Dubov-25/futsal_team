"""Smoke-тесты страниц фотогалереи.

Запуск:

    docker compose exec web pytest pytest_tests/web/test_gallery_pages.py
"""

import pytest
from django.urls import reverse
from rest_framework import status

from pytest_tests.factories import AlbumFactory


pytestmark = pytest.mark.django_db


def test_gallery_list_returns_200(client, album):
    """Страница галереи открывается."""
    response = client.get(reverse('web:gallery-list'))
    assert response.status_code == status.HTTP_200_OK


def test_gallery_list_shows_album(client, album):
    """Опубликованный альбом в списке."""
    response = client.get(reverse('web:gallery-list'))
    content = response.content.decode()
    assert album.title in content


def test_gallery_list_hides_unpublished(client, db):
    """Неопубликованный альбом скрыт."""

    hidden = AlbumFactory(
        title='Скрытый альбом',
        is_published=False,
    )
    response = client.get(reverse('web:gallery-list'))
    content = response.content.decode()
    assert hidden.title not in content


def test_album_detail_returns_200(client, album):
    """Детальная альбома открывается."""
    url = reverse('web:album-detail', args=[album.slug])
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


def test_album_detail_shows_title(client, album):
    """На детальной — заголовок альбома."""
    url = reverse('web:album-detail', args=[album.slug])
    response = client.get(url)
    content = response.content.decode()
    assert album.title in content


def test_album_detail_shows_photos(client, photo_in_album):
    """В альбоме видны фотографии."""
    url = reverse('web:album-detail', args=[photo_in_album.album.slug])
    response = client.get(url)
    content = response.content.decode()
    assert 'photo-item' in content


def test_album_detail_empty_state(client, album):
    """Альбом без фото — empty state."""
    url = reverse('web:album-detail', args=[album.slug])
    response = client.get(url)
    content = response.content.decode()
    assert 'В этом альбоме пока нет фотографий' in content


def test_album_detail_404_for_unpublished(client, db):
    """Неопубликованный альбом — 404."""

    hidden = AlbumFactory(title='Скрытый', is_published=False)
    url = reverse('web:album-detail', args=[hidden.slug])
    response = client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_album_detail_404_for_unknown_slug(client, db):
    """Несуществующий slug — 404."""
    url = reverse('web:album-detail', args=['nonexistent-slug'])
    response = client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
