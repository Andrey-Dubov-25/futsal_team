"""ViewSet матчей."""

from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from apps.api.v1.serializers import MatchSerializer
from apps.matches.models import Match


class MatchViewSet(viewsets.ModelViewSet):
    """CRUD-эндпоинт матчей + экшены upcoming и results."""

    queryset = Match.objects.prefetch_related('events__player').all()
    serializer_class = MatchSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        status = self.request.query_params.get('status')
        is_home = self.request.query_params.get('is_home')

        if status:
            qs = qs.filter(status=status)
        if is_home is not None:
            qs = qs.filter(is_home=is_home.lower() == 'true')
        return qs

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Ближайшие 5 матчей."""
        qs = (
            self.get_queryset()
            .filter(date__gte=timezone.now())
            .order_by('date')[:5]
        )
        return Response(self.get_serializer(qs, many=True).data)

    @action(detail=False, methods=['get'])
    def results(self, request):
        """Последние 10 завершённых матчей."""
        qs = self.get_queryset().filter(status=Match.Status.FINISHED)[:10]
        return Response(self.get_serializer(qs, many=True).data)
