"""Фикстуры для тестов API."""

import pytest

from apps.matches.models import MatchEvent
from apps.players.models import Player
from pytest_tests import constants as c
from pytest_tests.factories import (
    FinishedMatchFactory,
    MatchEventFactory,
    PlayerFactory,
)


@pytest.fixture
def sample_players(db):
    """Набор из трёх игроков разных позиций."""
    return [
        PlayerFactory(
            first_name='Иван',
            last_name='Вратарёв',
            number=1,
            position=Player.Position.GOALKEEPER,
        ),
        PlayerFactory(
            first_name='Пётр',
            last_name='Защитников',
            number=7,
            position=Player.Position.DEFENDER,
        ),
        PlayerFactory(
            first_name='Сергей',
            last_name='Голеадоров',
            number=10,
            position=Player.Position.FORWARD,
        ),
    ]


@pytest.fixture
def match_with_events(db, sample_players):
    """Завершённый матч 3:1 с событиями для тестов статистики."""
    match = FinishedMatchFactory(
        our_score=c.TEST_GOALS_SCORED,
        opponent_score=c.TEST_GOALS_CONCEDED,
    )
    forward = sample_players[2]
    defender = sample_players[1]

    MatchEventFactory(
        match=match,
        player=forward,
        event_type=MatchEvent.EventType.GOAL,
        minute=5,
    )
    MatchEventFactory(
        match=match,
        player=forward,
        event_type=MatchEvent.EventType.GOAL,
        minute=15,
    )
    MatchEventFactory(
        match=match,
        player=defender,
        event_type=MatchEvent.EventType.ASSIST,
        minute=5,
    )
    return match
