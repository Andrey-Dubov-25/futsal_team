"""ViewSet статистики игроков и команды."""

from django.db.models import Count, F, Q, Sum
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.api.v1.serializers.stats import (
    PlayerStatsSerializer,
    TeamStatsSerializer,
)
from apps.matches.models import Match
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

        data = [
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
            for player in players
        ]

        serializer = PlayerStatsSerializer(data, many=True)
        return Response(serializer.data)


class TeamStatsViewSet(viewsets.ViewSet):
    """Общая статистика команды.

    Публичный эндпоинт — доступен без авторизации.
    """

    permission_classes = [AllowAny]

    def list(self, request):
        """Сводка по завершённым матчам."""
        matches = Match.objects.filter(status=Match.Status.FINISHED)

        total = matches.count()
        won = matches.filter(our_score__gt=F('opponent_score')).count()
        lost = matches.filter(our_score__lt=F('opponent_score')).count()
        drawn = total - won - lost

        goals_scored = matches.aggregate(s=Sum('our_score'))['s'] or 0
        goals_conceded = matches.aggregate(s=Sum('opponent_score'))['s'] or 0

        avg_scored = round(goals_scored / total, 2) if total else 0.0
        avg_conceded = round(goals_conceded / total, 2) if total else 0.0
        win_rate = round(won / total * 100, 2) if total else 0.0

        # Форма: последние 5 матчей от новых к старым
        form = []
        for match in matches.order_by('-date')[:5]:
            if match.our_score > match.opponent_score:
                form.append('W')
            elif match.our_score < match.opponent_score:
                form.append('L')
            else:
                form.append('D')

        data = {
            'matches_total': total,
            'matches_won': won,
            'matches_drawn': drawn,
            'matches_lost': lost,
            'goals_scored': goals_scored,
            'goals_conceded': goals_conceded,
            'goal_difference': goals_scored - goals_conceded,
            'avg_goals_scored': avg_scored,
            'avg_goals_conceded': avg_conceded,
            'win_rate': win_rate,
            'form': form,
        }

        serializer = TeamStatsSerializer(data)
        return Response(serializer.data)
