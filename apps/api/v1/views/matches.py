"""ViewSet матчей."""

from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from apps.api.v1.filters import MatchFilter
from apps.api.v1.serializers import MatchSerializer
from apps.matches.models import Match


class MatchViewSet(viewsets.ModelViewSet):
    """CRUD-эндпоинт для матчей.

    Поддерживает фильтрацию, поиск и сортировку:
    - `?status=SCH`
    - `?is_home=true`
    - `?date_from=2026-01-01`
    - `?search=динамо`
    - `?ordering=-date`
    """

    queryset = Match.objects.prefetch_related('events__player').all()
    serializer_class = MatchSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_class = MatchFilter
    search_fields = ['opponent', 'location']
    ordering_fields = ['date', 'opponent']
    ordering = ['-date']

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Ближайшие 5 матчей."""
        qs = (
            self.get_queryset()
            .filter(date__gte=timezone.now())
            .order_by('date')[:5]
        )
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def results(self, request):
        """Последние 10 завершённых матчей."""
        qs = self.get_queryset().filter(
            status=Match.Status.FINISHED,
        )[:10]
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
