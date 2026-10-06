"""ViewSet статистики игроков."""

from django.db.models import Count, Q
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.api.v1.serializers.stats import PlayerStatsSerializer
from apps.players.models import Player


class PlayerStatsViewSet(viewsets.ViewSet):
    """Статистика игроков: голы, передачи, карточки.

    Публичный эндпоинт — доступен без авторизации.
    """

    permission_classes = [AllowAny]

    def list(self, request):
        """Список игроков со статистикой, отсортированный по очкам."""
        players = (
            Player.objects.filter(is_active=True)
            .annotate(
                goals=Count(
                    'events',
                    filter=Q(events__event_type='GOAL'),
                ),
                assists=Count(
                    'events',
                    filter=Q(events__event_type='ASSIST'),
                ),
                yellow_cards=Count(
                    'events',
                    filter=Q(events__event_type='YELLOW'),
                ),
                red_cards=Count(
                    'events',
                    filter=Q(events__event_type='RED'),
                ),
                matches_played=Count(
                    'events__match',
                    distinct=True,
                ),
            )
            .order_by('-goals', '-assists', 'number')
        )

        data = []
        for player in players:
            data.append(
                {
                    'id': player.id,
                    'full_name': f'{player.last_name} {player.first_name}',
                    'number': player.number,
                    'position': player.position,
                    'position_display': player.get_position_display(),
                    'goals': player.goals,
                    'assists': player.assists,
                    'yellow_cards': player.yellow_cards,
                    'red_cards': player.red_cards,
                    'matches_played': player.matches_played,
                    'points': player.goals + player.assists,
                }
            )

        serializer = PlayerStatsSerializer(data, many=True)
        return Response(serializer.data)
