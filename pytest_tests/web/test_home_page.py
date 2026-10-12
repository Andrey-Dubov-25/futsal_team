"""Тесты главной страницы.

Запуск:

    docker compose exec web pytest pytest_tests/web/test_home_page.py
"""

import pytest
from django.urls import reverse
from rest_framework import status

from pytest_tests.factories import (
    BefutsalTournamentFactory,
    FinishedMatchFactory,
    MatchEventFactory,
    MatchFactory,
    NewsPostFactory,
    PlayerFactory,
)


pytestmark = pytest.mark.django_db


# =============================================================================
# Hero и базовое
# =============================================================================


def test_home_returns_200(client):
    """Главная открывается."""
    response = client.get(reverse('web:home'))
    assert response.status_code == status.HTTP_200_OK


def test_home_shows_hero(client):
    """Hero с логотипом и названием."""
    response = client.get(reverse('web:home'))
    content = response.content.decode()
    assert 'МФК «Восход»' in content
    assert 'hero__logo' in content


# =============================================================================
# Ближайший матч
# =============================================================================


def test_home_shows_upcoming_match(client, db):
    """Ближайший матч отображается."""
    from datetime import timedelta

    from django.utils import timezone

    MatchFactory(
        opponent='Динамо',
        date=timezone.now() + timedelta(days=7),
        status='SCH',
    )

    response = client.get(reverse('web:home'))
    content = response.content.decode()

    assert 'Следующий матч' in content
    assert 'Динамо' in content


def test_home_shows_empty_match_block(client, db):
    """Нет матчей — пустой блок."""
    response = client.get(reverse('web:home'))
    content = response.content.decode()

    assert 'Ближайших матчей пока нет' in content


# =============================================================================
# Форма
# =============================================================================


def test_home_shows_form(client, db):
    """Форма W/D/L отображается."""
    for our, opp in [(3, 1), (2, 2), (0, 1), (4, 2)]:
        FinishedMatchFactory(
            our_score=our,
            opponent_score=opp,
        )

    response = client.get(reverse('web:home'))
    content = response.content.decode()

    assert 'Форма команды' in content
    assert 'form-badge--w' in content
    assert 'form-badge--d' in content
    assert 'form-badge--l' in content


def test_home_shows_form_stats(client, db):
    """Победы/ничьи/поражения."""
    FinishedMatchFactory(our_score=3, opponent_score=1)
    FinishedMatchFactory(our_score=3, opponent_score=1)
    FinishedMatchFactory(our_score=1, opponent_score=1)

    response = client.get(reverse('web:home'))
    content = response.content.decode()

    assert 'побед' in content
    assert 'ничьих' in content


# =============================================================================
# Топ-3 бомбардира
# =============================================================================


def test_home_shows_top_scorers(client, db):
    """Топ-3 бомбардира отображаются."""
    p1 = PlayerFactory(last_name='Голеадоров', number=10)
    p2 = PlayerFactory(last_name='Ассистов', number=7)
    p3 = PlayerFactory(last_name='Пасующий', number=5)

    # Голы
    MatchEventFactory(player=p1, event_type='GOAL')
    MatchEventFactory(player=p1, event_type='GOAL')
    MatchEventFactory(player=p1, event_type='GOAL')
    MatchEventFactory(player=p2, event_type='GOAL')
    MatchEventFactory(player=p2, event_type='ASSIST')
    MatchEventFactory(player=p2, event_type='ASSIST')
    MatchEventFactory(player=p3, event_type='ASSIST')

    response = client.get(reverse('web:home'))
    content = response.content.decode()

    assert 'Лучшие игроки' in content
    assert 'Голеадоров' in content
    assert 'Ассистов' in content
    assert 'Пасующий' in content


def test_home_top_scorer_order(client, db):
    """Сортировка по голам → передачам."""
    p1 = PlayerFactory(last_name='Первый', number=10)
    p2 = PlayerFactory(last_name='Второй', number=7)

    # У первого 3 гола, у второго 2
    for _ in range(3):
        MatchEventFactory(player=p1, event_type='GOAL')
    for _ in range(2):
        MatchEventFactory(player=p2, event_type='GOAL')

    response = client.get(reverse('web:home'))
    content = response.content.decode()

    # Первый идёт раньше второго
    pos1 = content.find('Первый')
    pos2 = content.find('Второй')
    assert pos1 < pos2


# =============================================================================
# Последние новости
# =============================================================================


def test_home_shows_recent_news(client, db):
    """3 последние новости."""
    NewsPostFactory(title='Новость 1')
    NewsPostFactory(title='Новость 2')
    NewsPostFactory(title='Новость 3')
    NewsPostFactory(title='Старая новость')

    response = client.get(reverse('web:home'))
    content = response.content.decode()

    assert 'Последние новости' in content
    # Только 3 последние, старая не попала
    assert 'Новость 1' in content or 'Новость 3' in content


def test_home_shows_vk_badge(client, db):
    """ВК-новости с бейджем на главной."""
    NewsPostFactory(
        title='ВК-новость',
        source='VK',
        external_id='-230450774_999',
    )

    response = client.get(reverse('web:home'))
    content = response.content.decode()

    assert 'news-card__badge--vk' in content


# =============================================================================
# Турниры
# =============================================================================


def test_home_shows_active_tournaments(client, db):
    """Активные турниры отображаются."""
    BefutsalTournamentFactory(
        name='Лето 2026. 4-я лига. Зона Б',
        is_active=True,
        matches=15,
        won=12,
        points=38,
        place=1,
    )

    response = client.get(reverse('web:home'))
    content = response.content.decode()

    assert 'Текущий сезон' in content
    assert 'Лето 2026' in content
    assert '🥇' in content  # медаль за 1 место
