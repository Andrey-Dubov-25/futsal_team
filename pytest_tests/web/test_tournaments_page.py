"""Smoke-тесты страницы турниров.

Запуск:

    docker compose exec web pytest pytest_tests/web/test_tournaments_page.py
"""

import pytest
from django.urls import reverse
from rest_framework import status

from pytest_tests.factories import (
    BefutsalSnapshotFactory,
    BefutsalTournamentFactory,
)


pytestmark = pytest.mark.django_db


def test_tournaments_page_returns_200(client, db):
    """Страница турниров открывается."""
    response = client.get(reverse('web:tournaments-list'))
    assert response.status_code == status.HTTP_200_OK


def test_tournaments_page_empty_state(client, db):
    """Без данных — empty state."""
    response = client.get(reverse('web:tournaments-list'))
    content = response.content.decode()
    assert 'Данные о турнирах пока не загружены' in content


def test_tournaments_page_shows_summary(client, db):
    """Сводка с годом и статистикой."""
    BefutsalSnapshotFactory(
        founded_year=2021,
        ranking_place=76,
        total_matches=205,
        total_won=99,
    )

    response = client.get(reverse('web:tournaments-list'))
    content = response.content.decode()

    assert '2021' in content
    assert '76' in content
    assert '205' in content
    assert '99' in content


def test_tournaments_page_shows_active(client, db):
    """Активные турниры отображаются."""
    BefutsalTournamentFactory(
        name='Лето 2026. 4-я лига. Зона Б',
        is_active=True,
        place=1,
        matches=15,
        won=12,
        points=38,
        percent=84,
    )

    response = client.get(reverse('web:tournaments-list'))
    content = response.content.decode()

    assert 'Текущий сезон' in content
    assert 'Лето 2026' in content
    assert '38' in content


def test_tournaments_page_shows_past(client, db):
    """Прошедшие турниры отображаются."""
    BefutsalTournamentFactory(
        name='Зима 2020-2021. 4-я лига Зона А',
        is_active=False,
        place=17,
    )

    response = client.get(reverse('web:tournaments-list'))
    content = response.content.decode()

    assert 'Прошедшие турниры' in content
    assert 'Зима 2020-2021' in content


def test_tournaments_page_shows_medals(client, db):
    """Медали для призёров."""
    BefutsalTournamentFactory(
        name='Лето 2026. 4-я лига. Зона Б',
        is_active=True,
        place=1,
    )

    response = client.get(reverse('web:tournaments-list'))
    content = response.content.decode()

    assert '🥇' in content


def test_tournaments_page_shows_befutsal_link(client, db):
    """Ссылка на Befutsal в футере."""
    response = client.get(reverse('web:tournaments-list'))
    content = response.content.decode()

    assert 'befutsal.ru' in content
    assert 'Полный профиль на Befutsal' in content


def test_tournaments_page_tournament_link(client, db):
    """Ссылка на турнир на Befutsal."""
    BefutsalTournamentFactory(
        name='Лето 2026',
        external_id='224668624',
        is_active=True,
    )

    response = client.get(reverse('web:tournaments-list'))
    content = response.content.decode()

    assert 'league.php?l=224668624' in content


def test_tournaments_page_shows_pinned_in_past(client, db):
    """Закреплённый турнир можно переместить в прошедшие."""
    BefutsalTournamentFactory(
        name='Закреплённый',
        is_active=False,
        is_pinned=True,
    )

    response = client.get(reverse('web:tournaments-list'))
    content = response.content.decode()

    assert 'Прошедшие турниры' in content
    assert 'Закреплённый' in content


def test_sync_does_not_touch_pinned(client, db, mocker, befutsal_html):
    """Sync не перезаписывает is_active у закреплённых."""
    from django.core.management import call_command

    from apps.league.models import BefutsalTournament

    mocker.patch(
        'apps.league.parser.fetch_page',
        return_value=befutsal_html,
    )

    # Первый sync — создаём турниры
    call_command('sync_befutsal')

    # Закрепляем один из активных и снимаем is_active
    t = BefutsalTournament.objects.get(external_id='224668624')
    t.is_active = False
    t.is_pinned = True
    t.save()

    # Повторный sync
    call_command('sync_befutsal')

    # Турнир остался неактивным (закреплён)
    t.refresh_from_db()
    assert t.is_active is False
    assert t.is_pinned is True
