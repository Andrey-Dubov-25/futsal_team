"""Тесты модели Training.

Запуск:

    docker compose exec web pytest pytest_tests/training/test_training_model.py
"""

import pytest

from apps.training.models import Training
from pytest_tests.factories import TrainingFactory


pytestmark = pytest.mark.model


def test_training_str_includes_title(past_training):
    """__str__ содержит название."""
    assert past_training.title in str(past_training)


def test_training_default_duration(db, head_coach):
    """Длительность по умолчанию — 90 минут."""

    training = TrainingFactory(coach=head_coach)
    assert training.duration_minutes == 90


def test_training_coach_optional(db):
    """coach — необязательное поле."""

    training = TrainingFactory(coach=None)
    assert training.coach is None


def test_training_ordering_by_date_desc(db, past_training, upcoming_training):
    """Свежие тренировки сверху."""
    dates = list(Training.objects.values_list('date', flat=True))
    assert dates == sorted(dates, reverse=True)


def test_cancelled_training_flag(cancelled_training):
    """Отменённая тренировка помечена."""
    assert cancelled_training.is_cancelled is True
