"""Smoke-тесты страниц новостей.

Запуск:

    docker compose exec web pytest pytest_tests/web/test_news_pages.py
"""

import pytest
from django.urls import reverse
from rest_framework import status

from apps.news.models import Comment


pytestmark = pytest.mark.django_db


def test_news_list_returns_200(client, published_news):
    """Страница новостей открывается."""
    response = client.get(reverse('web:news-list'))
    assert response.status_code == status.HTTP_200_OK


def test_news_list_shows_published(client, published_news):
    """Опубликованная новость в списке."""
    response = client.get(reverse('web:news-list'))
    content = response.content.decode()
    assert published_news.title in content


def test_news_list_hides_drafts(client, draft_news):
    """Черновик не отображается в списке."""
    response = client.get(reverse('web:news-list'))
    content = response.content.decode()
    assert draft_news.title not in content


def test_news_detail_returns_200(client, published_news):
    """Детальная новости открывается."""
    url = reverse('web:news-detail', args=[published_news.slug])
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


def test_news_detail_shows_content(client, published_news):
    """На детальной — заголовок и текст."""
    url = reverse('web:news-detail', args=[published_news.slug])
    response = client.get(url)
    content = response.content.decode()
    assert published_news.title in content
    assert published_news.content in content


def test_news_detail_404_for_draft(client, draft_news):
    """Черновик по URL — 404."""
    url = reverse('web:news-detail', args=[draft_news.slug])
    response = client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_news_detail_shows_comments(client, comment_on_news):
    """Комментарии отображаются."""
    url = reverse(
        'web:news-detail',
        args=[comment_on_news.post.slug],
    )
    response = client.get(url)
    content = response.content.decode()
    assert comment_on_news.text in content


def test_news_detail_shows_login_prompt_for_anonymous(
    client,
    published_news,
):
    """Анониму — приглашение войти, а не форма."""
    url = reverse('web:news-detail', args=[published_news.slug])
    response = client.get(url)
    content = response.content.decode()
    assert 'Войдите' in content


def test_news_detail_shows_form_for_authenticated(
    client,
    user,
    published_news,
):
    """Авторизованному — форма комментария."""
    client.force_login(user)
    url = reverse('web:news-detail', args=[published_news.slug])
    response = client.get(url)
    content = response.content.decode()
    assert 'comment-form' in content


def test_add_comment_requires_login(client, published_news):
    """POST комментария без логина — редирект на login."""
    url = reverse('web:news-add-comment', args=[published_news.slug])
    response = client.post(url, {'text': 'Тест'})
    assert response.status_code == status.HTTP_302_FOUND


def test_add_comment_creates_and_returns_html(
    client,
    user,
    published_news,
):
    """POST комментария создаёт и возвращает HTML."""
    client.force_login(user)
    url = reverse('web:news-add-comment', args=[published_news.slug])
    response = client.post(url, {'text': 'Отличная новость!'})

    assert response.status_code == status.HTTP_200_OK
    assert 'Отличная новость!' in response.content.decode()

    assert Comment.objects.filter(
        post=published_news,
        author=user,
        text='Отличная новость!',
    ).exists()


def test_add_empty_comment_shows_error(
    client,
    user,
    published_news,
):
    """Пустой комментарий — ошибка в HTML."""
    client.force_login(user)
    url = reverse('web:news-add-comment', args=[published_news.slug])
    response = client.post(url, {'text': '   '})

    assert response.status_code == status.HTTP_200_OK
    content = response.content.decode()
    assert 'не может быть пустым' in content
