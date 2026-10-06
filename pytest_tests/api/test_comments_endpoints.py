"""Тесты API комментариев.

Запуск:

    docker compose exec web pytest pytest_tests/api/test_comments_endpoints.py
"""

import pytest
from rest_framework import status

from pytest_tests.factories import CommentFactory


pytestmark = pytest.mark.api


def test_anonymous_can_list_comments(api_client, comment_on_news):
    """GET списка комментариев доступен анонимно."""
    response = api_client.get('/api/v1/comments/')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] >= 1


def test_list_comments_filtered_by_post(
    api_client,
    published_news,
    comment_on_news,
):
    """?post=<slug> фильтрует по новости."""
    response = api_client.get(
        f'/api/v1/comments/?post={published_news.slug}',
    )
    assert response.status_code == status.HTTP_200_OK
    for item in response.data['results']:
        assert item['post_slug'] == published_news.slug


def test_create_comment_requires_auth(api_client, published_news):
    """POST без авторизации — 401."""
    response = api_client.post(
        '/api/v1/comments/',
        {'text': 'Комментарий', 'post': published_news.slug},
        format='json',
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_comment_with_auth(auth_client, published_news):
    """POST с авторизацией — 201, автор проставлен автоматически."""
    response = auth_client.post(
        '/api/v1/comments/',
        {'text': 'Отличный матч!', 'post': published_news.slug},
        format='json',
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['text'] == 'Отличный матч!'
    assert response.data['author']['username']
    assert response.data['post_slug'] == published_news.slug


def test_create_empty_comment_fails(auth_client, published_news):
    """Пустой текст — 400."""
    response = auth_client.post(
        '/api/v1/comments/',
        {'text': '   ', 'post': published_news.slug},
        format='json',
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_create_too_long_comment_fails(auth_client, published_news):
    """Слишком длинный текст — 400."""
    from pytest_tests import constants as c

    response = auth_client.post(
        '/api/v1/comments/',
        {
            'text': 'X' * (c.COMMENT_TEXT_MAX_LENGTH + 1),
            'post': published_news.slug,
        },
        format='json',
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_author_can_delete_own_comment(auth_client, comment_on_news):
    """Автор удаляет свой комментарий — 204."""
    response = auth_client.delete(
        f'/api/v1/comments/{comment_on_news.id}/',
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_other_user_cannot_delete_comment(
    api_client,
    comment_on_news,
    another_user,
):
    """Другой пользователь удалить чужой — 403."""
    api_client.force_authenticate(user=another_user)
    response = api_client.delete(
        f'/api/v1/comments/{comment_on_news.id}/',
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_admin_can_delete_any_comment(
    admin_client,
    comment_on_news,
):
    """Админ удаляет любой комментарий — 204."""
    response = admin_client.delete(
        f'/api/v1/comments/{comment_on_news.id}/',
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_hidden_comment_not_in_list(db, api_client, published_news, user):
    """Неопубликованный комментарий скрыт из списка."""
    CommentFactory(
        post=published_news,
        author=user,
        text='Скрытый',
        is_published=False,
    )
    response = api_client.get('/api/v1/comments/')
    texts = [item['text'] for item in response.data['results']]
    assert 'Скрытый' not in texts


def test_comments_ordered_desc(api_client, published_news, user):
    """Свежие комментарии — сверху."""
    CommentFactory(post=published_news, author=user, text='Первый')
    CommentFactory(post=published_news, author=user, text='Второй')

    response = api_client.get('/api/v1/comments/')
    texts = [item['text'] for item in response.data['results']]
    assert texts.index('Второй') < texts.index('Первый')
