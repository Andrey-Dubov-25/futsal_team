"""Парсер постов из группы ВКонтакте.

Использует VK API (метод wall.get). Возвращает структурированные
данные — без записи в БД. Запись выполняет команда sync_vk.
"""

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime

import requests

from config import constants as c


logger = logging.getLogger(__name__)


class VkParseError(Exception):
    """Ошибка парсинга ВКонтакте."""


# =============================================================================
# Data-классы
# =============================================================================


@dataclass
class ParsedVkPost:
    """Один пост из ВК, готовый к сохранению в NewsPost."""

    external_id: str  # -230450774_330
    external_url: str  # https://vk.com/wall-230450774_330
    title: str  # первая строка, обрезанная до 100
    content: str  # полный текст
    excerpt: str  # краткое описание
    cover_url: str | None  # URL обложки (максимальный размер)
    has_video: bool  # есть ли видео
    published_at: datetime  # дата поста (с таймзоной)


@dataclass
class ParsedVkFeed:
    """Результат парсинга стены группы."""

    posts: list[ParsedVkPost] = field(default_factory=list)
    total_count: int = 0


# =============================================================================
# Загрузка через VK API
# =============================================================================


def fetch_wall(
    owner_id: int | None = None,
    count: int | None = None,
    access_token: str | None = None,
) -> dict:
    """Загрузить посты со стены группы через VK API.

    Возвращает сырой ответ API (словарь с ключом response).
    """
    owner_id = owner_id if owner_id is not None else c.VK_GROUP_OWNER_ID
    count = count or c.VK_POSTS_COUNT
    token = access_token or _get_token()

    if not token:
        raise VkParseError(
            'VK_ACCESS_TOKEN не задан. Установите переменную окружения.',
        )

    url = f'{c.VK_API_BASE_URL}/wall.get'
    params = {
        'owner_id': owner_id,
        'count': count,
        'access_token': token,
        'v': c.VK_API_VERSION,
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=c.VK_REQUEST_TIMEOUT,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise VkParseError(f'Ошибка запроса к VK API: {exc}') from exc

    data = response.json()

    if 'error' in data:
        error = data['error']
        raise VkParseError(
            f'VK API вернул ошибку: '
            f'{error.get("error_code")} — {error.get("error_msg")}',
        )

    return data


def _get_token() -> str:
    """Получить токен из настроек Django."""
    from django.conf import settings

    return getattr(settings, 'VK_ACCESS_TOKEN', '') or ''


# =============================================================================
# Извлечение данных из поста
# =============================================================================


def _extract_title(text: str) -> str:
    """Заголовок — первая строка текста, до 100 символов."""
    if not text:
        return ''

    # Первая непустая строка
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if not lines:
        return ''

    first_line = lines[0]

    # Обрезка с многоточием
    if len(first_line) > c.VK_TITLE_MAX_LENGTH:
        first_line = first_line[: c.VK_TITLE_MAX_LENGTH - 3] + '...'

    return first_line


def _extract_excerpt(text: str) -> str:
    """Краткое описание — первые ~300 символов после первой строки."""
    if not text:
        return ''

    # Убираем первую строку
    lines = text.split('\n')
    rest = '\n'.join(lines[1:]).strip()

    if not rest:
        return ''

    # До 300 символов
    excerpt = rest[:300]
    if len(rest) > 300:
        excerpt = excerpt[:297] + '...'

    return excerpt


def _find_photo_url(attachments: list) -> str | None:
    """Найти URL самого большого фото в списке вложений."""
    for att in attachments:
        if att.get('type') == 'photo':
            photo = att.get('photo', {})
            sizes = photo.get('sizes', [])
            if not sizes:
                continue

            # Ищем самый большой размер (type='w' или 'z')
            # Сортировка по площади
            best = max(
                sizes,
                key=lambda s: s.get('width', 0) * s.get('height', 0),
            )
            return best.get('url')

    return None


def _find_video_preview_url(attachments: list) -> str | None:
    """Найти превью видео (для постов без фото)."""
    for att in attachments:
        if att.get('type') == 'video':
            video = att.get('video', {})
            images = video.get('image', [])
            if not images:
                continue

            # Самый большой размер
            best = max(
                images,
                key=lambda img: img.get('width', 0) * img.get('height', 0),
            )
            return best.get('url')

    return None


def _has_video(attachments: list) -> bool:
    """Есть ли видео в списке вложений."""
    return any(att.get('type') == 'video' for att in attachments)


def _extract_cover(post: dict) -> str | None:
    """Извлечь URL обложки поста.

    Порядок поиска:
    1. Своё фото в attachments
    2. Фото в copy_history[0].attachments (репост)
    3. Превью видео в attachments
    4. Превью видео в copy_history[0].attachments
    """
    own_attachments = post.get('attachments', [])
    copy_history = post.get('copy_history', [])
    repost_attachments = (
        copy_history[0].get('attachments', []) if copy_history else []
    )

    # 1. Своё фото
    url = _find_photo_url(own_attachments)
    if url:
        return url

    # 2. Фото из репоста
    url = _find_photo_url(repost_attachments)
    if url:
        return url

    # 3. Превью своего видео
    url = _find_video_preview_url(own_attachments)
    if url:
        return url

    # 4. Превью видео из репоста
    url = _find_video_preview_url(repost_attachments)
    if url:
        return url

    return None


def _has_video_in_post(post: dict) -> bool:
    """Есть ли видео — в своих вложениях или в репосте."""
    own = post.get('attachments', [])
    if _has_video(own):
        return True

    copy_history = post.get('copy_history', [])
    if copy_history:
        repost = copy_history[0].get('attachments', [])
        if _has_video(repost):
            return True

    return False


def _parse_post(post: dict) -> ParsedVkPost | None:
    """Распарсить один пост. Вернуть None, если поста нет смысла хранить."""
    text = post.get('text', '').strip()

    # Пропускаем посты без текста
    if not text:
        return None

    post_id = post.get('id')
    owner_id = post.get('owner_id')
    if not post_id or not owner_id:
        return None

    # Формируем ID и URL
    external_id = f'{owner_id}_{post_id}'
    external_url = c.VK_POST_LINK.format(
        owner_id=owner_id,
        post_id=post_id,
    )

    # Заголовок и описание
    title = _extract_title(text)
    if not title:
        return None

    excerpt = _extract_excerpt(text)

    # Обложка
    cover_url = _extract_cover(post)

    # Видео
    has_video = _has_video_in_post(post)

    # Дата
    date_unix = post.get('date')
    if not date_unix:
        return None

    published_at = datetime.fromtimestamp(
        date_unix,
        tz=UTC,
    )

    return ParsedVkPost(
        external_id=external_id,
        external_url=external_url,
        title=title,
        content=text,
        excerpt=excerpt,
        cover_url=cover_url,
        has_video=has_video,
        published_at=published_at,
    )


# =============================================================================
# Публичная функция — парсит всю стену
# =============================================================================


def parse_wall(
    owner_id: int | None = None,
    count: int | None = None,
) -> ParsedVkFeed:
    """Спарсить последние посты со стены группы."""
    data = fetch_wall(owner_id=owner_id, count=count)

    response = data.get('response', {})
    items = response.get('items', [])
    total_count = response.get('count', 0)

    posts = []
    skipped = 0

    for item in items:
        parsed = _parse_post(item)
        if parsed:
            posts.append(parsed)
        else:
            skipped += 1

    logger.info(
        'VK: получено %d постов, распарсено %d, пропущено %d',
        len(items),
        len(posts),
        skipped,
    )

    return ParsedVkFeed(posts=posts, total_count=total_count)
