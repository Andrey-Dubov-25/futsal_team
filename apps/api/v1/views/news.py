"""ViewSet новостей."""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from apps.api.v1.serializers import NewsPostSerializer
from apps.news.models import NewsPost


class NewsPostViewSet(viewsets.ModelViewSet):
    """CRUD-эндпоинт новостей. URL — по slug."""

    queryset = NewsPost.objects.select_related('author').filter(
        is_published=True
    )
    serializer_class = NewsPostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
