"""Тесты модели NewsPost.

Запуск:

    docker compose exec web pytest pytest_tests/news/test_news_model.py
"""

import pytest

from apps.news.models import NewsPost


pytestmark = pytest.mark.model


def test_news_str_returns_title(published_news):
    """__str__ возвращает заголовок."""
    assert str(published_news) == published_news.title


def test_news_slug_is_generated(db):
    """Слаг генерируется из заголовка и транслитерируется в ASCII."""
    news = NewsPost.objects.create(
        title='Победа над Динамо',
        content='Текст',
    )
    assert news.slug != ''
    assert news.slug == 'pobeda-nad-dinamo'


def test_news_slug_is_ascii_only(db):
    """Slug содержит только ASCII-символы."""
    news = NewsPost.objects.create(
        title='Победа над Динамо',
        content='Текст',
    )
    assert news.slug.isascii()


def test_news_slug_fallback_when_title_has_no_letters(db):
    """Если из title не выходит slug — используем fallback."""
    news = NewsPost.objects.create(
        title='🎉🎉🎉',
        content='Текст',
    )
    assert news.slug != ''
    assert news.slug.startswith('news-')


def test_news_author_is_optional(db):
    """Автор — необязательное поле."""
    news = NewsPost.objects.create(
        title='Без автора',
        content='Текст',
    )
    assert news.author is None


def test_news_is_published_default_true(db):
    """Опубликовано по умолчанию — True."""
    news = NewsPost.objects.create(
        title='Тест',
        content='Текст',
    )
    assert news.is_published is True
