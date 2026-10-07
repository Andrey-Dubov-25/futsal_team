"""Smoke-тесты страницы тренировок.

Запуск:

    docker compose exec web pytest pytest_tests/web/test_training_pages.py
"""

import pytest
from django.urls import reverse
from rest_framework import status


pytestmark = pytest.mark.django_db


def test_trainings_list_returns_200(client, upcoming_training):
    """Страница тренировок открывается."""
    response = client.get(reverse('web:trainings-list'))
    assert response.status_code == status.HTTP_200_OK


def test_trainings_list_shows_upcoming(client, upcoming_training):
    """Будущая тренировка отображается в списке."""
    response = client.get(reverse('web:trainings-list'))
    content = response.content.decode()
    assert upcoming_training.title in content


def test_trainings_list_shows_past(client, past_training):
    """Прошедшая тренировка отображается."""
    response = client.get(reverse('web:trainings-list'))
    content = response.content.decode()
    assert past_training.title in content


def test_trainings_list_hides_cancelled_from_upcoming(
    client,
    cancelled_training,
):
    """Отменённая тренировка не попадает в «Ближайшие»."""
    response = client.get(reverse('web:trainings-list'))
    content = response.content.decode()

    # «Ближайшие» идут до «Прошедших» — проверяем порядок
    past_pos = content.find('Прошедшие тренировки')
    cancelled_pos = content.find(cancelled_training.title)

    # Если тренировка вообще есть — она должна быть в блоке «Прошедшие»
    if cancelled_pos != -1:
        assert cancelled_pos > past_pos


def test_trainings_list_shows_coach(client, upcoming_training):
    """Тренер отображается."""
    response = client.get(reverse('web:trainings-list'))
    content = response.content.decode()
    assert upcoming_training.coach.last_name in content


def test_trainings_list_empty_states(client, db):
    """Без тренировок — оба empty state."""
    response = client.get(reverse('web:trainings-list'))
    content = response.content.decode()

    assert 'Ближайших тренировок пока нет' in content
    assert 'Прошедших тренировок нет' in content
