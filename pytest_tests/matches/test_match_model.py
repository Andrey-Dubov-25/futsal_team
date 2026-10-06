"""Тесты моделей Match и MatchEvent.

Запуск:

    docker compose exec web pytest pytest_tests/matches/test_match_model.py
"""

from datetime import timedelta

import pytest
from django.utils import timezone

from apps.matches.models import Match, MatchEvent
from pytest_tests import constants as c
from pytest_tests.factories import MatchFactory


pytestmark = pytest.mark.model


def test_match_str_includes_opponent(finished_match):
    """__str__ содержит соперника."""
    assert finished_match.opponent in str(finished_match)


def test_match_status_default_is_scheduled(scheduled_match):
    """Статус по умолчанию — запланирован."""
    assert scheduled_match.status == Match.Status.SCHEDULED


def test_finished_match_has_scores(finished_match):
    """У завершённого матча заполнены счета."""
    assert finished_match.our_score == c.TEST_GOALS_SCORED
    assert finished_match.opponent_score == c.TEST_GOALS_CONCEDED


def test_match_status_display(finished_match):
    """get_status_display возвращает 'Завершён'."""
    assert finished_match.get_status_display() == 'Завершён'


def test_match_ordering_by_date_desc(db):
    """Матчи сортируются по дате (свежие сверху)."""

    MatchFactory(date=timezone.now() - timedelta(days=10))
    MatchFactory(date=timezone.now())

    dates = list(Match.objects.values_list('date', flat=True))
    assert dates == sorted(dates, reverse=True)


def test_match_event_links_match_and_player(goal_event):
    """Событие связано с матчем и игроком."""
    assert goal_event.event_type == MatchEvent.EventType.GOAL
    assert goal_event.minute == c.TEST_EVENT_MINUTE
    assert goal_event in goal_event.match.events.all()
    assert goal_event in goal_event.player.events.all()
