"""Фильтры для новостей."""

import django_filters as filters

from apps.news.models import NewsPost


class NewsPostFilter(filters.FilterSet):
    """Фильтр новостей: автор, диапазон дат публикации."""

    author = filters.NumberFilter(field_name='author_id')
    published_from = filters.DateTimeFilter(
        field_name='published_at',
        lookup_expr='gte',
    )
    published_to = filters.DateTimeFilter(
        field_name='published_at',
        lookup_expr='lte',
    )

    class Meta:
        model = NewsPost
        fields = ['author', 'is_published']
