"""Smoke-тесты страницы тренерского состава.

Запуск:

    docker compose exec web pytest pytest_tests/web/test_staff_pages.py
"""

import pytest
from django.urls import reverse
from rest_framework import status

from apps.staff.models import Staff
from pytest_tests.factories import StaffFactory


pytestmark = pytest.mark.django_db


def test_staff_list_returns_200(client, head_coach):
    """Страница тренерского состава открывается."""
    response = client.get(reverse('web:staff-list'))
    assert response.status_code == status.HTTP_200_OK


def test_staff_list_shows_active_members(client, head_coach):
    """Активные сотрудники отображаются."""
    response = client.get(reverse('web:staff-list'))
    content = response.content.decode()

    assert head_coach.last_name in content
    assert head_coach.first_name in content


def test_staff_list_shows_role(client, head_coach):
    """Роль сотрудника отображается."""
    response = client.get(reverse('web:staff-list'))
    content = response.content.decode()

    assert head_coach.get_role_display() in content


def test_staff_list_hides_inactive(client, db):
    """Неактивные сотрудники не отображаются."""

    inactive = StaffFactory(
        first_name='Неактивный',
        last_name='Сотрудник',
        role=Staff.Role.OTHER,
        is_active=False,
    )
    response = client.get(reverse('web:staff-list'))
    content = response.content.decode()

    assert inactive.last_name not in content


def test_staff_list_empty_state(client, db):
    """Без сотрудников — empty state."""
    response = client.get(reverse('web:staff-list'))
    content = response.content.decode()

    assert 'Информация о составе пока не заполнена' in content


def test_staff_list_shows_contact_info(client, db):
    """Контакты отображаются."""

    member = StaffFactory(
        first_name='Иван',
        last_name='Тренеров',
        role=Staff.Role.HEAD_COACH,
        phone='+79990001122',
        email='coach@example.com',
    )
    response = client.get(reverse('web:staff-list'))
    content = response.content.decode()

    assert member.phone in content
    assert member.email in content
