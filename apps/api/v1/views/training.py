"""ViewSet тренировок."""

from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from apps.api.v1.serializers import TrainingSerializer
from apps.training.models import Training


class TrainingViewSet(viewsets.ModelViewSet):
    """CRUD-эндпоинт тренировок.

    Фильтры:
    - `?is_cancelled=true`
    - `?date_from=2026-01-01`
    - `?date_to=2026-12-31`
    """

    queryset = Training.objects.select_related('coach').all()
    serializer_class = TrainingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_fields = ['is_cancelled']
    search_fields = ['title', 'location']
    ordering_fields = ['date', 'title']
    ordering = ['-date']

    def get_queryset(self):
        qs = super().get_queryset()
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')

        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)
        return qs

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Ближайшие 5 тренировок (не отменённых)."""
        qs = (
            self.get_queryset()
            .filter(date__gte=timezone.now(), is_cancelled=False)
            .order_by('date')[:5]
        )
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
