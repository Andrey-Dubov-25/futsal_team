"""Парсер страницы команды на befutsal.ru.

Возвращает структурированные данные — без записи в БД.
Запись выполняет management command sync_befutsal.
"""

import logging
import re
from dataclasses import dataclass, field

import requests
from bs4 import BeautifulSoup

from config import constants as c


logger = logging.getLogger(__name__)


class BefutsalParseError(Exception):
    """Ошибка парсинга страницы Befutsal."""


# =============================================================================
# Data-классы (что возвращает парсер)
# =============================================================================


@dataclass
class ParsedClubInfo:
    """Профиль и общая статистика команды."""

    founded_year: int | None = None
    ranking_place: int | None = None
    total_matches: int = 0
    total_won: int = 0
    total_drawn: int = 0
    total_lost: int = 0
    total_goals_scored: int = 0
    total_goals_conceded: int = 0


@dataclass
class ParsedTournament:
    """Один турнир из таблицы выступлений."""

    name: str
    external_id: str | None = None
    season: str = ''
    competition: str = ''
    matches: int = 0
    won: int = 0
    drawn: int = 0
    lost: int = 0
    goals_scored: int = 0
    goals_conceded: int = 0
    points: int = 0
    percent: int | None = None
    place: int | None = None
    order: int = 0


@dataclass
class ParsedClubPage:
    """Всё, что удалось спарсить со страницы."""

    info: ParsedClubInfo = field(default_factory=ParsedClubInfo)
    tournaments: list[ParsedTournament] = field(default_factory=list)


# =============================================================================
# Загрузка HTML
# =============================================================================


def fetch_page(url: str | None = None) -> str:
    """Загрузить HTML страницы с Befutsal.

    Возвращает декодированный HTML или бросает BefutsalParseError.
    """
    url = url or c.BEFUTSAL_CLUB_URL

    try:
        response = requests.get(
            url,
            timeout=c.BEFUTSAL_REQUEST_TIMEOUT,
            headers={'User-Agent': c.BEFUTSAL_USER_AGENT},
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise BefutsalParseError(
            f'Не удалось загрузить {url}: {exc}',
        ) from exc

    response.encoding = 'utf-8'
    return response.text


# =============================================================================
# Утилиты парсинга
# =============================================================================


def _to_int(value: str) -> int:
    """Преобразовать строку в int, пустую — в 0."""
    value = value.strip()
    if not value:
        return 0
    try:
        return int(value)
    except ValueError:
        return 0


def _to_optional_int(value: str) -> int | None:
    """Преобразовать строку в int, пустую — в None."""
    value = value.strip()
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _split_season_and_competition(name: str) -> tuple[str, str]:
    """Разделить полное название турнира на сезон и соревнование.

    'Лето 2026. 4-я лига. Зона Б' → ('Лето 2026', '4-я лига. Зона Б')
    'ВСЕГО' → ('', '')
    'Лето 2026' → ('Лето 2026', '')
    """
    parts = name.split('. ', 1)
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()
    return name.strip(), ''


# =============================================================================
# Парсинг профиля и общей статистики
# =============================================================================


def parse_club_info(soup: BeautifulSoup) -> ParsedClubInfo:
    """Вытащить год основания, рейтинг и общую статистику."""
    info = ParsedClubInfo()
    page_text = soup.get_text(' ', strip=True)

    # Год основания: 'Основана: 2021'
    match = re.search(r'Основана[:\s]*(\d{4})', page_text)
    if match:
        info.founded_year = int(match.group(1))

    # Место в рейтинге: '76 лучшее место в рейтинге'
    match = re.search(
        r'(\d+)\s*лучшее место в рейтинге',
        page_text,
        re.IGNORECASE,
    )
    if match:
        info.ranking_place = int(match.group(1))

    # Игры, победы, ничьи, поражения
    match = re.search(
        r'Игр\s*(\d+).*?Побед\s*(\d+).*?Ничьих\s*(\d+).*?Поражений\s*(\d+)',
        page_text,
        re.DOTALL,
    )
    if match:
        info.total_matches = int(match.group(1))
        info.total_won = int(match.group(2))
        info.total_drawn = int(match.group(3))
        info.total_lost = int(match.group(4))

    # Голы
    match = re.search(
        r'Забито\s*(\d+).*?Пропущено\s*(\d+)',
        page_text,
        re.DOTALL,
    )
    if match:
        info.total_goals_scored = int(match.group(1))
        info.total_goals_conceded = int(match.group(2))

    return info


# =============================================================================
# Парсинг таблицы турниров
# =============================================================================


def _extract_external_id(row) -> str | None:
    """Извлечь ID турнира из onclick строки таблицы.

    <tr onclick="window.location.href='league.php?l=224668624';">
        → '224668624'
    """
    onclick = row.get('onclick', '')
    match = re.search(r'league\.php\?l=(\d+)', onclick)
    if match:
        return match.group(1)
    return None


def parse_tournaments(soup: BeautifulSoup) -> list[ParsedTournament]:
    """Распарсить таблицу выступлений по турнирам."""
    tables = soup.find_all('table')
    if not tables:
        raise BefutsalParseError('Не найдено ни одной таблицы на странице')

    table = tables[0]
    rows = table.find_all('tr')

    if len(rows) < 2:
        raise BefutsalParseError('Таблица выступлений пуста')

    tournaments: list[ParsedTournament] = []

    # Первая строка — заголовки, пропускаем
    for order, row in enumerate(rows[1:]):
        cells = row.find_all(['td', 'th'])
        if len(cells) < 8:
            logger.warning(
                'Пропущена строка с %d ячейками: %s',
                len(cells),
                row.get_text(' ', strip=True)[:80],
            )
            continue

        name = cells[0].get_text(' ', strip=True)

        # Пропускаем строку «ВСЕГО»
        if name.upper() == 'ВСЕГО':
            continue

        # И, В, Н, П
        matches = _to_int(cells[1].get_text(strip=True))
        won = _to_int(cells[2].get_text(strip=True))
        drawn = _to_int(cells[3].get_text(strip=True))
        lost = _to_int(cells[4].get_text(strip=True))

        # Мячи: '88-30'
        goals_text = cells[5].get_text(strip=True)
        goals_match = re.match(r'(\d+)\s*-\s*(\d+)', goals_text)
        if goals_match:
            goals_scored = int(goals_match.group(1))
            goals_conceded = int(goals_match.group(2))
        else:
            goals_scored = 0
            goals_conceded = 0

        # Очки: '38(84%)' → points=38, percent=84
        points_text = cells[6].get_text(' ', strip=True)
        points = 0
        percent = None
        points_match = re.match(r'(\d+)', points_text)
        if points_match:
            points = int(points_match.group(1))
        percent_match = re.search(r'\((\d+)%\)', points_text)
        if percent_match:
            percent = int(percent_match.group(1))

        # Место: '1', '4', '' (для кубков)
        place_text = cells[7].get_text(strip=True)
        place = _to_optional_int(place_text)

        season, competition = _split_season_and_competition(name)

        tournaments.append(
            ParsedTournament(
                name=name,
                external_id=_extract_external_id(row),
                season=season,
                competition=competition,
                matches=matches,
                won=won,
                drawn=drawn,
                lost=lost,
                goals_scored=goals_scored,
                goals_conceded=goals_conceded,
                points=points,
                percent=percent,
                place=place,
                order=order,
            )
        )

    return tournaments


# =============================================================================
# Публичная функция — парсит всё за один вызов
# =============================================================================


def parse_club_page(url: str | None = None) -> ParsedClubPage:
    """Спарсить страницу команды и вернуть структурированные данные."""
    html = fetch_page(url)
    soup = BeautifulSoup(html, 'html.parser')

    info = parse_club_info(soup)
    tournaments = parse_tournaments(soup)

    # Отмечаем активные турниры: у них нет места (соревнование идёт)
    # либо совпадает с текущим сезоном.
    if tournaments:
        # Активные — турниры без места (в процессе) на верхних позициях
        for t in tournaments[:5]:
            if t.place is None:
                # Не помечаем автоматом — определит команда
                pass

    logger.info(
        'Парсинг успешен: %d турниров, год=%s, игр=%d',
        len(tournaments),
        info.founded_year,
        info.total_matches,
    )

    return ParsedClubPage(info=info, tournaments=tournaments)
