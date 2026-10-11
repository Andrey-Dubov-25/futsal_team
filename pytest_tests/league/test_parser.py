"""Тесты парсера befutsal.ru.

Запуск:

    docker compose exec web pytest pytest_tests/league/test_parser.py

Особенности:
    - Тесты используют сохранённый HTML (fixtures/befutsal_club.html),
      поэтому не ходят в сеть.
    - Быстрые, работают в CI без интернета.
"""

import pytest
from bs4 import BeautifulSoup

from apps.league import parser


pytestmark = pytest.mark.django_db


# =============================================================================
# fetch_page
# =============================================================================


def test_fetch_page_returns_html(mock_fetch_page, befutsal_html):
    """fetch_page возвращает HTML страницы."""
    html = parser.fetch_page()
    assert html == befutsal_html
    assert 'МФК Восход' in html


def test_fetch_page_handles_connection_error(mocker):
    """При сетевой ошибке — BefutsalParseError."""
    import requests

    mocker.patch(
        'apps.league.parser.requests.get',
        side_effect=requests.ConnectionError('Network is down'),
    )

    with pytest.raises(parser.BefutsalParseError) as exc:
        parser.fetch_page()

    assert 'Не удалось загрузить' in str(exc.value)


# =============================================================================
# parse_club_info
# =============================================================================


def test_parse_club_info_extracts_profile(befutsal_html):
    """Парсим год основания и место в рейтинге."""
    soup = BeautifulSoup(befutsal_html, 'html.parser')
    info = parser.parse_club_info(soup)

    assert info.founded_year == 2021
    assert info.ranking_place == 76


def test_parse_club_info_extracts_total_stats(befutsal_html):
    """Парсим общую статистику."""
    soup = BeautifulSoup(befutsal_html, 'html.parser')
    info = parser.parse_club_info(soup)

    assert info.total_matches == 205
    assert info.total_won == 99
    assert info.total_drawn == 25
    assert info.total_lost == 81
    assert info.total_goals_scored == 859
    assert info.total_goals_conceded == 695


def test_parse_club_info_handles_missing_fields():
    """Если данных нет — возвращаются дефолтные значения."""
    soup = BeautifulSoup('<html><body>пусто</body></html>', 'html.parser')
    info = parser.parse_club_info(soup)

    assert info.founded_year is None
    assert info.ranking_place is None
    assert info.total_matches == 0
    assert info.total_won == 0


# =============================================================================
# parse_tournaments
# =============================================================================


def test_parse_tournaments_returns_all(befutsal_html):
    """Находим все 18 турниров."""
    soup = BeautifulSoup(befutsal_html, 'html.parser')
    tournaments = parser.parse_tournaments(soup)

    assert len(tournaments) == 18


def test_parse_tournaments_first_is_latest_season(befutsal_html):
    """Первый турнир — самый свежий сезон."""
    soup = BeautifulSoup(befutsal_html, 'html.parser')
    tournaments = parser.parse_tournaments(soup)

    first = tournaments[0]
    assert 'Лето 2026' in first.name
    assert first.order == 0
    assert first.matches == 15
    assert first.won == 12
    assert first.drawn == 2
    assert first.lost == 1


def test_parse_tournaments_extracts_goals(befutsal_html):
    """Мячи разделены на забитые и пропущенные."""
    soup = BeautifulSoup(befutsal_html, 'html.parser')
    tournaments = parser.parse_tournaments(soup)

    first = tournaments[0]
    assert first.goals_scored == 88
    assert first.goals_conceded == 30


def test_parse_tournaments_extracts_points_and_percent(befutsal_html):
    """Очки и процент из "38(84%)"."""
    soup = BeautifulSoup(befutsal_html, 'html.parser')
    tournaments = parser.parse_tournaments(soup)

    first = tournaments[0]
    assert first.points == 38
    assert first.percent == 84


def test_parse_tournaments_extracts_place(befutsal_html):
    """Место — 1 для первого турнира."""
    soup = BeautifulSoup(befutsal_html, 'html.parser')
    tournaments = parser.parse_tournaments(soup)

    first = tournaments[0]
    assert first.place == 1


def test_parse_tournaments_extracts_external_id(befutsal_html):
    """ID турнира — из onclick."""
    soup = BeautifulSoup(befutsal_html, 'html.parser')
    tournaments = parser.parse_tournaments(soup)

    first = tournaments[0]
    assert first.external_id == '224668624'


def test_parse_tournaments_handles_cups_without_place(befutsal_html):
    """Кубки могут не иметь места — None."""
    soup = BeautifulSoup(befutsal_html, 'html.parser')
    tournaments = parser.parse_tournaments(soup)

    # Находим турнир без места
    no_place = [t for t in tournaments if t.place is None]
    assert len(no_place) > 0

    # Среди них — кубки
    cup_names = [t.name for t in no_place]
    assert any('Кубок' in name for name in cup_names)


def test_parse_tournaments_splits_season_and_competition(befutsal_html):
    """Название разделяется на сезон и соревнование."""
    soup = BeautifulSoup(befutsal_html, 'html.parser')
    tournaments = parser.parse_tournaments(soup)

    first = tournaments[0]
    assert first.season == 'Лето 2026'
    assert '4-я лига' in first.competition


def test_parse_tournaments_raises_on_empty_table():
    """Если таблицы нет — BefutsalParseError."""
    soup = BeautifulSoup('<html><body></body></html>', 'html.parser')

    with pytest.raises(parser.BefutsalParseError):
        parser.parse_tournaments(soup)


def test_parse_tournaments_skips_total_row(befutsal_html):
    """Строка ВСЕГО не попадает в список."""
    soup = BeautifulSoup(befutsal_html, 'html.parser')
    tournaments = parser.parse_tournaments(soup)

    names = [t.name for t in tournaments]
    assert 'ВСЕГО' not in names


# =============================================================================
# parse_club_page (интеграционный)
# =============================================================================


def test_parse_club_page_returns_full_data(mock_fetch_page):
    """parse_club_page возвращает и профиль, и турниры."""
    page = parser.parse_club_page()

    assert page.info.founded_year == 2021
    assert page.info.total_matches == 205
    assert len(page.tournaments) == 18


# =============================================================================
# Утилиты
# =============================================================================


def test_to_int_handles_empty():
    """Пустая строка → 0."""
    assert parser._to_int('') == 0
    assert parser._to_int('  ') == 0


def test_to_int_handles_number():
    """Число → int."""
    assert parser._to_int('15') == 15
    assert parser._to_int(' 42 ') == 42


def test_to_int_handles_invalid():
    """Невалидное → 0."""
    assert parser._to_int('abc') == 0


def test_to_optional_int_handles_empty():
    """Пустая строка → None."""
    assert parser._to_optional_int('') is None
    assert parser._to_optional_int('  ') is None


def test_to_optional_int_handles_number():
    """Число → int."""
    assert parser._to_optional_int('1') == 1


def test_split_season_and_competition():
    """Разделение названия."""
    season, comp = parser._split_season_and_competition(
        'Лето 2026. 4-я лига. Зона Б',
    )
    assert season == 'Лето 2026'
    assert comp == '4-я лига. Зона Б'


def test_split_season_and_competition_no_dot():
    """Без точки — всё в сезон."""
    season, comp = parser._split_season_and_competition('Лето 2026')
    assert season == 'Лето 2026'
    assert comp == ''
