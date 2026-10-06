"""ViewSet'ы фотогалереи."""

from django.db.models import Count
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from apps.api.v1.serializers import (
    AlbumDetailSerializer,
    AlbumListSerializer,
    PhotoSerializer,
)
from apps.gallery.models import Album, Photo


class AlbumViewSet(viewsets.ModelViewSet):
    """CRUD-эндпоинт альбомов.

    Фильтры:
    - `?is_published=true`
    - `?date_from=2026-01-01`
    - `?date_to=2026-12-31`
    - `?match=<id>`
    - `?search=<название>`
    """

    serializer_class = AlbumListSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    filterset_fields = ['is_published', 'match']
    search_fields = ['title', 'description']
    ordering_fields = ['date', 'order']
    ordering = ['-date', 'order']

    def get_queryset(self):
        qs = Album.objects.select_related('match').annotate(
            photos_count=Count('photos')
        )
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')

        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)
        return qs

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AlbumDetailSerializer
        return AlbumListSerializer


class PhotoViewSet(viewsets.ModelViewSet):
    """CRUD-эндпоинт фотографий.

    Фильтры:
    - `?album=<id>`
    """

    queryset = Photo.objects.select_related('album').all()
    serializer_class = PhotoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_fields = ['album']
    ordering_fields = ['order', 'uploaded_at']
    ordering = ['order', 'id']
