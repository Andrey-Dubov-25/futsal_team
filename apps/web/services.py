"""Сервисы для веб-страниц — бизнес-логика, отделённая от view."""

from django.db.models import Count, F, Q, Sum

from apps.matches.models import Match
from apps.players.models import Player


def get_player_stats():
    """Статистика игроков: голы, передачи, карточки.

    Возвращает queryset Player с аннотациями:
    goals, assists, yellow_cards, red_cards, matches_played.
    """
    return (
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


def get_team_stats():
    """Общая статистика команды по завершённым матчам."""
    matches = Match.objects.filter(
        status=Match.Status.FINISHED,
        our_score__isnull=False,
        opponent_score__isnull=False,
    )

    total = matches.count()
    won = matches.filter(our_score__gt=F('opponent_score')).count()
    lost = matches.filter(our_score__lt=F('opponent_score')).count()
    drawn = total - won - lost

    goals_scored = matches.aggregate(s=Sum('our_score'))['s'] or 0
    goals_conceded = (
        matches.aggregate(
            s=Sum('opponent_score'),
        )['s']
        or 0
    )

    avg_scored = round(goals_scored / total, 2) if total else 0.0
    avg_conceded = round(goals_conceded / total, 2) if total else 0.0
    win_rate = round(won / total * 100, 2) if total else 0.0

    form = []
    for match in matches.order_by('-date')[:5]:
        if match.our_score > match.opponent_score:
            form.append('W')
        elif match.our_score < match.opponent_score:
            form.append('L')
        else:
            form.append('D')

    return {
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
