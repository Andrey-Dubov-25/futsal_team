"""Тесты API фотогалереи.

Запуск:

    docker compose exec web pytest pytest_tests/api/test_gallery_endpoints.py
"""

import pytest
from rest_framework import status

from apps.gallery.models import Album


pytestmark = pytest.mark.api


def test_list_albums_returns_200(api_client, album):
    """GET списка альбомов — 200."""
    response = api_client.get('/api/v1/albums/')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 1


def test_album_detail_has_photos(api_client, photo_in_album):
    """GET детали — есть массив photos."""
    response = api_client.get(
        f'/api/v1/albums/{photo_in_album.album.slug}/',
    )
    assert response.status_code == status.HTTP_200_OK
    assert 'photos' in response.data
    assert len(response.data['photos']) == 1


def test_album_list_has_photos_count(api_client, photo_in_album):
    """В списке — поле photos_count."""
    response = api_client.get('/api/v1/albums/')
    item = response.data['results'][0]
    assert item['photos_count'] == 1


def test_filter_albums_by_is_published(api_client, album, db):
    """?is_published=true фильтрует."""
    Album.objects.create(
        title='Черновик',
        date='2026-10-01',
        is_published=False,
    )
    response = api_client.get('/api/v1/albums/?is_published=true')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 1


def test_search_albums_by_title(api_client, album):
    """?search= находит альбом по названию."""
    response = api_client.get('/api/v1/albums/?search=Динамо')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] >= 1


def test_ordering_albums_by_date(api_client, db):
    """?ordering=-date сортирует по дате (свежие сверху)."""
    Album.objects.create(title='Старый', date='2020-01-01')
    Album.objects.create(title='Новый', date='2026-01-01')

    response = api_client.get('/api/v1/albums/?ordering=-date')
    dates = [item['date'] for item in response.data['results']]
    assert dates == sorted(dates, reverse=True)


def test_create_album_requires_auth(api_client):
    """POST без авторизации — 401."""
    response = api_client.post(
        '/api/v1/albums/',
        {'title': 'X', 'date': '2026-10-01'},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_album_with_auth(auth_client):
    """POST с авторизацией — 201, slug сгенерирован."""
    response = auth_client.post(
        '/api/v1/albums/',
        {
            'title': 'Новый альбом',
            'date': '2026-10-01',
        },
        format='json',
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['title'] == 'Новый альбом'
    assert response.data['slug'] != ''


def test_filter_photos_by_album(api_client, photo_in_album):
    """?album=<id> фильтрует фото по альбому."""
    response = api_client.get(
        f'/api/v1/photos/?album={photo_in_album.album.id}',
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 1


def test_list_photos_returns_200(api_client, photo_in_album):
    """GET списка фото — 200."""
    response = api_client.get('/api/v1/photos/')
    assert response.status_code == status.HTTP_200_OK


def test_create_photo_requires_auth(api_client, album):
    """POST фото без авторизации — 401."""
    response = api_client.post(
        '/api/v1/photos/',
        {'album': album.id, 'caption': 'Тест'},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
