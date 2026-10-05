"""ViewSet игроков."""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from apps.api.v1.filters import PlayerFilter
from apps.api.v1.serializers import PlayerSerializer
from apps.players.models import Player


class PlayerViewSet(viewsets.ModelViewSet):
    """CRUD-эндпоинт для игроков.

    Поддерживает фильтрацию, поиск и сортировку:
    - `?position=GK`
    - `?is_active=true`
    - `?number=10`
    - `?birth_date_from=2000-01-01`
    - `?search=иван`
    - `?ordering=-number`
    """

    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_class = PlayerFilter
    search_fields = ['first_name', 'last_name', 'nickname']
    ordering_fields = ['number', 'last_name', 'birth_date']
    ordering = ['number']
