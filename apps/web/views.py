"""View-функции для HTML-страниц."""

from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from apps.matches.models import Match
from apps.players.models import Player


def home(request):
    """Главная страница."""
    return render(request, 'home.html')


def players_list(request):
    """Список всех активных игроков."""
    players = Player.objects.filter(is_active=True).order_by('number')
    return render(request, 'players/list.html', {'players': players})


def player_detail(request, pk):
    """Детальная страница игрока."""
    player = get_object_or_404(
        Player.objects.prefetch_related('events__match'),
        pk=pk,
        is_active=True,
    )
    events = player.events.all().order_by('-match__date')[:10]
    return render(
        request,
        'players/detail.html',
        {'player': player, 'events': events},
    )


def matches_list(request):
    """Список матчей: ближайшие и прошедшие."""
    now = timezone.now()

    upcoming = Match.objects.filter(
        date__gte=now, status=Match.Status.SCHEDULED
    ).order_by('date')
    results = Match.objects.filter(status=Match.Status.FINISHED).order_by(
        '-date'
    )[:20]

    return render(
        request,
        'matches/list.html',
        {'upcoming': upcoming, 'results': results},
    )


def match_detail(request, pk):
    """Детальная страница матча."""
    match = get_object_or_404(
        Match.objects.prefetch_related('events__player'),
        pk=pk,
    )
    events = match.events.all().order_by('minute')
    return render(
        request,
        'matches/detail.html',
        {'match': match, 'events': events},
    )
