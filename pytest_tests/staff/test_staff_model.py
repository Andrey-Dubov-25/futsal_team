"""Тесты модели Staff.

Запуск:

    docker compose exec web pytest pytest_tests/staff/test_staff_model.py
"""

import pytest

from apps.staff.models import Staff
from pytest_tests.factories import StaffFactory


pytestmark = pytest.mark.model


def test_staff_str_includes_name_and_role(head_coach):
    """__str__ содержит ФИО и должность."""
    result = str(head_coach)
    assert head_coach.last_name in result
    assert head_coach.first_name in result
    assert 'Главный тренер' in result


def test_staff_full_name_property(head_coach):
    """full_name — одной строкой."""
    assert head_coach.full_name == (
        f'{head_coach.last_name} {head_coach.first_name}'
    )


def test_staff_role_display(assistant_coach):
    """get_role_display корректный."""
    assert assistant_coach.get_role_display() == 'Ассистент'


def test_staff_ordering_by_order(db):
    """Сортировка по order, потом по фамилии."""

    StaffFactory(order=5, last_name='Второй')
    StaffFactory(order=1, last_name='Первый')
    StaffFactory(order=3, last_name='Третий')

    orders = list(Staff.objects.values_list('order', flat=True))
    assert orders == sorted(orders)


def test_staff_user_optional(db):
    """user — необязательное поле."""

    staff = StaffFactory()
    assert staff.user is None
