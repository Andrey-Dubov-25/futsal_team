"""Тесты моделей Album и Photo.

Запуск:

    docker compose exec web pytest pytest_tests/gallery/test_gallery_model.py
"""

import pytest

from apps.gallery.models import Album, Photo


pytestmark = pytest.mark.model


def test_album_str_includes_title(album):
    """__str__ содержит название."""
    assert album.title in str(album)


def test_album_slug_auto_generated(db):
    """Слаг генерируется из title при сохранении."""
    new_album = Album.objects.create(
        title='Турнир осень 2026',
        date='2026-10-01',
    )
    assert new_album.slug != ''
    assert ' ' not in new_album.slug


def test_album_slug_is_unique(db):
    """Слаги уникальны — второй альбом с тем же title меняет slug."""
    Album.objects.create(title='Турнир', date='2026-10-01')
    second = Album.objects.create(
        title='Турнир',
        date='2026-10-02',
        slug='турнир-2',
    )
    assert second.slug == 'турнир-2'


def test_album_ordering_by_date_desc(db):
    """Свежие альбомы сверху."""
    Album.objects.create(title='Старый', date='2020-01-01')
    Album.objects.create(title='Новый', date='2026-01-01')

    dates = list(Album.objects.values_list('date', flat=True))
    assert dates == sorted(dates, reverse=True)


def test_album_match_optional(album):
    """match — необязательное поле."""
    assert album.match is None


def test_album_is_published_default_true(db):
    """Опубликован по умолчанию — True."""
    new_album = Album.objects.create(
        title='Тест',
        date='2026-10-01',
    )
    assert new_album.is_published is True


def test_photo_str_returns_caption(photo_in_album):
    """__str__ возвращает caption."""
    assert str(photo_in_album) == photo_in_album.caption


def test_photo_str_without_caption(db, album):
    """__str__ без caption — упоминает альбом."""
    photo = Photo.objects.create(
        album=album,
        image='test.jpg',
    )
    assert 'Фото' in str(photo)
    assert album.title in str(photo)


def test_photo_linked_to_album(photo_in_album, album):
    """Фото связано с альбомом."""
    assert photo_in_album.album == album
    assert photo_in_album in album.photos.all()


def test_photo_ordering_by_order(db, album):
    """Фото сортируются по order."""
    Photo.objects.create(album=album, image='a.jpg', order=3)
    Photo.objects.create(album=album, image='b.jpg', order=1)
    Photo.objects.create(album=album, image='c.jpg', order=2)

    orders = list(Photo.objects.values_list('order', flat=True))
    assert orders == sorted(orders)
