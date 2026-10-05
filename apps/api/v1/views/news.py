"""ViewSet новостей."""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from apps.api.v1.filters import NewsPostFilter
from apps.api.v1.serializers import NewsPostSerializer
from apps.news.models import NewsPost


class NewsPostViewSet(viewsets.ModelViewSet):
    """CRUD-эндпоинт для новостей.

    Поддерживает фильтрацию, поиск и сортировку:
    - `?author=1`
    - `?published_from=2026-01-01`
    - `?search=победа`
    - `?ordering=-published_at`
    """

    queryset = NewsPost.objects.select_related('author').filter(
        is_published=True,
    )
    serializer_class = NewsPostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    filterset_class = NewsPostFilter
    search_fields = ['title', 'excerpt', 'content']
    ordering_fields = ['published_at', 'title']
    ordering = ['-published_at']
