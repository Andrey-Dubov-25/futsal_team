"""ViewSet игроков."""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from apps.api.v1.serializers import PlayerSerializer
from apps.players.models import Player


class PlayerViewSet(viewsets.ModelViewSet):
    """CRUD-эндпоинт для игроков с фильтрацией по позиции и активности."""

    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        position = self.request.query_params.get('position')
        is_active = self.request.query_params.get('is_active')

        if position:
            qs = qs.filter(position=position)
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() == 'true')
        return qs
