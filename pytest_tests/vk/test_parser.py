"""Тесты парсера ВКонтакте.

Запуск:

    docker compose exec web pytest pytest_tests/vk/test_parser.py

Тесты используют мок VK API — не ходят в реальный ВК.
"""

import pytest

from apps.vk import parser


pytestmark = pytest.mark.django_db


# =============================================================================
# fetch_wall
# =============================================================================


def test_fetch_wall_returns_data(mock_vk_api, settings):
    """fetch_wall возвращает данные от API."""
    settings.VK_ACCESS_TOKEN = 'test-token'

    data = parser.fetch_wall()

    assert 'response' in data
    assert data['response']['count'] == 164


def test_fetch_wall_without_token(mocker, settings):
    """Без токена — ошибка."""
    settings.VK_ACCESS_TOKEN = ''

    with pytest.raises(parser.VkParseError) as exc:
        parser.fetch_wall()

    assert 'VK_ACCESS_TOKEN не задан' in str(exc.value)


def test_fetch_wall_handles_api_error(mocker, settings):
    """Если VK API вернул error — VkParseError."""
    settings.VK_ACCESS_TOKEN = 'test-token'

    class MockResponse:
        def json(self):
            return {'error': {'error_code': 5, 'error_msg': 'Auth failed'}}

        def raise_for_status(self):
            pass

    mocker.patch(
        'apps.vk.parser.requests.get',
        return_value=MockResponse(),
    )

    with pytest.raises(parser.VkParseError) as exc:
        parser.fetch_wall()

    assert 'Auth failed' in str(exc.value)


# =============================================================================
# _extract_title
# =============================================================================


def test_extract_title_first_line():
    """Заголовок — первая строка."""
    text = '⚽⚽⚽ Голы за сезон ⚽⚽⚽\n\nОт самых простых...'
    title = parser._extract_title(text)
    assert title == '⚽⚽⚽ Голы за сезон ⚽⚽⚽'


def test_extract_title_skips_empty_lines():
    """Пустые строки в начале пропускаются."""
    text = '\n\n\n  Первая строка\n\nВторая'
    title = parser._extract_title(text)
    assert title == 'Первая строка'


def test_extract_title_truncates_long():
    """Длинный заголовок обрезается до 100 символов."""
    text = 'X' * 200
    title = parser._extract_title(text)

    assert len(title) == 100
    assert title.endswith('...')


def test_extract_title_empty_text():
    """Пустой текст — пустой заголовок."""
    assert parser._extract_title('') == ''
    assert parser._extract_title('   ') == ''


# =============================================================================
# _extract_cover
# =============================================================================


def test_extract_cover_own_photo():
    """Своё фото — приоритет."""
    post = {
        'attachments': [
            {
                'type': 'photo',
                'photo': {
                    'sizes': [
                        {'width': 100, 'height': 100, 'url': 'small.jpg'},
                        {'width': 1000, 'height': 1000, 'url': 'big.jpg'},
                    ],
                },
            }
        ],
    }
    assert parser._extract_cover(post) == 'big.jpg'


def test_extract_cover_from_repost():
    """Если своё пусто — берём из репоста."""
    post = {
        'attachments': [],
        'copy_history': [
            {
                'attachments': [
                    {
                        'type': 'photo',
                        'photo': {
                            'sizes': [
                                {
                                    'width': 1000,
                                    'height': 1000,
                                    'url': 'repost.jpg',
                                },
                            ],
                        },
                    }
                ],
            }
        ],
    }
    assert parser._extract_cover(post) == 'repost.jpg'


def test_extract_cover_video_preview():
    """Если фото нет — превью видео."""
    post = {
        'attachments': [
            {
                'type': 'video',
                'video': {
                    'image': [
                        {'width': 100, 'height': 100, 'url': 'small.jpg'},
                        {'width': 1280, 'height': 720, 'url': 'preview.jpg'},
                    ],
                },
            }
        ],
    }
    assert parser._extract_cover(post) == 'preview.jpg'


def test_extract_cover_none():
    """Нет вложений — None."""
    assert parser._extract_cover({}) is None
    assert parser._extract_cover({'attachments': []}) is None


# =============================================================================
# _parse_post
# =============================================================================


def test_parse_post_basic():
    """Базовый пост с текстом."""
    post = {
        'id': 123,
        'owner_id': -230450774,
        'date': 1790171008,
        'text': 'Заголовок\n\nОписание',
        'attachments': [],
    }
    parsed = parser._parse_post(post)

    assert parsed is not None
    assert parsed.external_id == '-230450774_123'
    assert parsed.external_url == 'https://vk.com/wall-230450774_123'
    assert parsed.title == 'Заголовок'
    assert parsed.content == 'Заголовок\n\nОписание'
    assert parsed.has_video is False
    assert parsed.cover_url is None


def test_parse_post_empty_text():
    """Пустой текст — None."""
    post = {
        'id': 123,
        'owner_id': -230450774,
        'date': 1790171008,
        'text': '',
    }
    assert parser._parse_post(post) is None


def test_parse_post_has_video():
    """Есть видео — флаг True."""
    post = {
        'id': 123,
        'owner_id': -230450774,
        'date': 1790171008,
        'text': 'Пост с видео\n\nОписание',
        'attachments': [{'type': 'video', 'video': {}}],
    }
    parsed = parser._parse_post(post)
    assert parsed.has_video is True


def test_parse_post_video_in_repost():
    """Видео в репосте — тоже учитываем."""
    post = {
        'id': 123,
        'owner_id': -230450774,
        'date': 1790171008,
        'text': 'Пост\n\nОписание',
        'attachments': [],
        'copy_history': [
            {
                'attachments': [{'type': 'video', 'video': {}}],
            }
        ],
    }
    parsed = parser._parse_post(post)
    assert parsed.has_video is True


# =============================================================================
# parse_wall (интеграция)
# =============================================================================


def test_parse_wall_integration(mock_vk_api, settings):
    """parse_wall возвращает все посты с текстом."""
    settings.VK_ACCESS_TOKEN = 'test-token'

    feed = parser.parse_wall()

    # 4 поста, но один без текста — пропущен
    assert len(feed.posts) == 3
    assert feed.total_count == 164

    # Первый пост — с видео в репосте
    first = feed.posts[0]
    assert first.external_id == '-230450774_330'
    assert first.has_video is True
    assert first.cover_url == 'https://example.com/big.jpg'
