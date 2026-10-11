"""Фикстуры для тестов приложения league."""

import pytest


@pytest.fixture
def mock_fetch_page(mocker, befutsal_html):
    """Мок fetch_page — возвращает сохранённый HTML.

    Патчит requests.get в парсере, чтобы тесты не ходили в сеть.
    """
    return mocker.patch(
        'apps.league.parser.fetch_page',
        return_value=befutsal_html,
    )
