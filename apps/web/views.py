"""View-функции для HTML-страниц."""

from django.shortcuts import get_object_or_404, render

from apps.players.models import Player


def home(request):
    """Главная страница."""
    return render(request, 'home.html')


def players_list(request):
    """Список всех активных игроков."""
    players = Player.objects.filter(is_active=True).order_by('number')
    context = {
        'players': players,
    }
    return render(request, 'players/list.html', context)


def player_detail(request, pk):
    """Детальная страница игрока."""
    player = get_object_or_404(
        Player.objects.prefetch_related('events__match'),
        pk=pk,
        is_active=True,
    )
    context = {
        'player': player,
        'events': player.events.all().order_by('-match__date')[:10],
    }
    return render(request, 'players/detail.html', context)
