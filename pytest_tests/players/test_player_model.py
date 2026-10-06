"""Тесты модели Player.

Запуск:

    docker compose exec web pytest pytest_tests/players/test_player_model.py

Подробный вывод:

    docker compose exec web pytest pytest_tests/players/test_player_model.py -v
"""

import pytest
from django.db import IntegrityError

from apps.players.models import Player


pytestmark = pytest.mark.model


def test_player_str_includes_number_and_name(forward):
    """__str__ включает номер, фамилию и имя."""
    assert (
        str(forward)
        == f'#{forward.number} {forward.last_name} {forward.first_name}'
    )


def test_player_str_without_number_shows_dash(db):
    """__str__ без номера показывает прочерк."""
    player = Player.objects.create(
        first_name='Тест',
        last_name='Тестов',
        position=Player.Position.FORWARD,
    )
    assert str(player) == '#— Тестов Тест'


def test_player_position_display(goalkeeper):
    """get_position_display возвращает 'Вратарь'."""
    assert goalkeeper.get_position_display() == 'Вратарь'


def test_player_is_active_default_true(db):
    """По умолчанию игрок активен."""
    player = Player.objects.create(
        first_name='Тест',
        last_name='Тестов',
        position=Player.Position.FORWARD,
    )
    assert player.is_active is True


def test_player_number_is_unique(forward):
    """Номер игрока уникален — повторный insert падает."""
    with pytest.raises(IntegrityError):
        Player.objects.create(
            first_name='Другой',
            last_name='Игрок',
            number=forward.number,
            position=Player.Position.DEFENDER,
        )


def test_player_ordering_by_number(db):
    """По умолчанию игроки сортируются по номеру."""
    from pytest_tests.factories import PlayerFactory

    PlayerFactory(number=10)
    PlayerFactory(number=1)
    PlayerFactory(number=7)

    numbers = list(Player.objects.values_list('number', flat=True))
    assert numbers == sorted(numbers)
