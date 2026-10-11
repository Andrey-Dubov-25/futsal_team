"""Тесты management command sync_befutsal.

Запуск:

    docker compose exec web pytest pytest_tests/league/test_sync_command.py

Тесты используют мок парсера — не ходят в сеть.
"""

import pytest
from django.core.management import call_command

from apps.league.models import BefutsalSnapshot, BefutsalTournament
from apps.league.parser import BefutsalParseError


pytestmark = pytest.mark.django_db


# =============================================================================
# Базовые сценарии
# =============================================================================


def test_sync_creates_snapshot(mock_fetch_page):
    """Sync создаёт снимок статистики."""
    call_command('sync_befutsal')

    assert BefutsalSnapshot.objects.count() == 1
    snapshot = BefutsalSnapshot.objects.first()

    assert snapshot.founded_year == 2021
    assert snapshot.ranking_place == 76
    assert snapshot.total_matches == 205
    assert snapshot.total_won == 99


def test_sync_creates_tournaments(mock_fetch_page):
    """Sync создаёт все 18 турниров."""
    call_command('sync_befutsal')

    assert BefutsalTournament.objects.count() == 18


def test_sync_marks_active_tournaments(mock_fetch_page):
    """Активные турниры — сезон «Лето 2026»."""
    call_command('sync_befutsal')

    active = BefutsalTournament.objects.filter(is_active=True)
    assert active.count() == 4

    # Все активные — из сезона «Лето 2026»
    seasons = set(active.values_list('season', flat=True))
    assert seasons == {'Лето 2026'}


# =============================================================================
# Идемпотентность
# =============================================================================


def test_sync_is_idempotent(mock_fetch_page):
    """Второй запуск не создаёт дубли."""
    call_command('sync_befutsal')
    call_command('sync_befutsal')

    assert BefutsalSnapshot.objects.count() == 1  # не дублируется
    assert BefutsalTournament.objects.count() == 18  # не дублируется


def test_sync_does_not_create_duplicate_snapshot(mock_fetch_page):
    """Снимок не создаётся повторно, если статистика не изменилась."""
    call_command('sync_befutsal')
    first_snapshot = BefutsalSnapshot.objects.first()

    call_command('sync_befutsal')
    second_snapshot = BefutsalSnapshot.objects.first()

    # Должен быть тот же снимок (не создался новый)
    assert second_snapshot.id == first_snapshot.id


def test_sync_updates_existing_tournaments(mock_fetch_page):
    """Существующий турнир обновляется, не создаётся заново."""
    call_command('sync_befutsal')

    # Меняем название у турнира
    t = BefutsalTournament.objects.get(external_id='224668624')
    t.name = 'Старое название'
    t.save()

    # Запускаем синк заново
    call_command('sync_befutsal')

    # Название вернулось к значению из парсера
    t.refresh_from_db()
    assert t.name == 'Лето 2026. 4-я лига. Зона Б'


# =============================================================================
# --dry-run
# =============================================================================


def test_sync_dry_run_does_not_write(mock_fetch_page):
    """--dry-run не пишет в БД."""
    call_command('sync_befutsal', '--dry-run')

    assert BefutsalSnapshot.objects.count() == 0
    assert BefutsalTournament.objects.count() == 0


# =============================================================================
# Обработка ошибок
# =============================================================================


def test_sync_handles_parse_error(mocker, capsys):
    """При ошибке парсинга — sync не падает, пишет ошибку."""

    mocker.patch(
        'apps.league.management.commands.sync_befutsal.parse_club_page',
        side_effect=BefutsalParseError('Тестовая ошибка'),
    )

    call_command('sync_befutsal')

    captured = capsys.readouterr()
    assert 'Ошибка парсинга' in captured.err

    # В БД ничего не попало
    assert BefutsalTournament.objects.count() == 0
