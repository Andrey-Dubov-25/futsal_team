"""Фикстуры для тестов приложения league."""

from pathlib import Path

import pytest


# Путь к сохранённому HTML с befutsal.ru
FIXTURES_DIR = Path(__file__).parent / 'fixtures'
BEFUTSAL_HTML_PATH = FIXTURES_DIR / 'befutsal_club.html'


@pytest.fixture
def befutsal_html():
    """Реальный HTML страницы команды с befutsal.ru.

    Сохранён один раз в fixtures/befutsal_club.html.
    Используется в тестах для парсинга без сетевых запросов.
    """
    if not BEFUTSAL_HTML_PATH.exists():
        pytest.skip(
            f'Фикстура не найдена: {BEFUTSAL_HTML_PATH}. '
            'Запустите: python -c "from apps.league.parser '
            'import fetch_page; ..."',
        )
    return BEFUTSAL_HTML_PATH.read_text(encoding='utf-8')


@pytest.fixture
def mock_fetch_page(mocker, befutsal_html):
    """Мок fetch_page — возвращает сохранённый HTML.

    Патчит requests.get в парсере, чтобы тесты не ходили в сеть.
    """
    return mocker.patch(
        'apps.league.parser.fetch_page',
        return_value=befutsal_html,
    )
