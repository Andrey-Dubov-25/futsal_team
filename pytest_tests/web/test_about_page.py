"""Smoke-тесты страницы «О клубе».

Запуск:

    docker compose exec web pytest pytest_tests/web/test_about_page.py
"""

import pytest
from django.urls import reverse
from rest_framework import status

from pytest_tests.factories import BefutsalSnapshotFactory


pytestmark = pytest.mark.django_db


def test_about_page_returns_200(client):
    """Страница открывается."""
    response = client.get(reverse('web:about'))
    assert response.status_code == status.HTTP_200_OK


def test_about_page_shows_club_name(client):
    """В hero — название команды."""
    response = client.get(reverse('web:about'))
    content = response.content.decode()
    assert 'МФК «Восход»' in content


def test_about_page_shows_stats(client):
    """Карточки со статистикой."""
    BefutsalSnapshotFactory(
        founded_year=2021,
        ranking_place=76,
        total_matches=205,
        total_won=99,
        total_goals_scored=859,
        total_goals_conceded=695,
    )

    response = client.get(reverse('web:about'))
    content = response.content.decode()

    assert '2021' in content
    assert '76' in content
    assert '205' in content
    assert '99' in content
    assert '859' in content
    assert '695' in content


def test_about_page_shows_win_rate(client):
    """Процент побед отображается."""
    BefutsalSnapshotFactory(
        total_matches=205,
        total_won=99,
    )

    response = client.get(reverse('web:about'))
    content = response.content.decode()

    assert '48.3' in content  # win_rate


def test_about_page_shows_history(client):
    """История клуба отображается."""
    response = client.get(reverse('web:about'))
    content = response.content.decode()

    assert 'История клуба' in content
    # Кусочек текста из истории
    assert '2021' in content


def test_about_page_shows_contacts(client):
    """Контакты отображаются."""
    response = client.get(reverse('web:about'))
    content = response.content.decode()

    assert 'Связаться с нами' in content
    assert 'vk.ru/voshodchane' in content


def test_about_page_shows_befutsal_link(client):
    """Ссылка на Befutsal внизу."""
    response = client.get(reverse('web:about'))
    content = response.content.decode()

    assert 'befutsal.ru/club.php' in content
    assert 'Профиль на Befutsal' in content


def test_about_page_without_snapshot(client):
    """Без снимка — страница работает, но без статистики."""
    response = client.get(reverse('web:about'))
    content = response.content.decode()

    assert response.status_code == status.HTTP_200_OK
    # Всё равно есть hero и история
    assert 'МФК «Восход»' in content
