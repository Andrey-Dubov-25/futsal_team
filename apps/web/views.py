"""View-функции для HTML-страниц."""

from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.gallery.models import Album
from apps.matches.models import Match
from apps.news.models import NewsPost
from apps.players.models import Player
from apps.staff.models import Staff

from .forms import CommentForm
from .services import get_player_stats, get_team_stats


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


def news_list(request):
    """Список опубликованных новостей."""
    news = (
        NewsPost.objects.filter(is_published=True)
        .select_related('author')
        .order_by('-published_at')
    )
    return render(request, 'news/list.html', {'news': news})


def news_detail(request, slug):
    """Детальная страница новости с комментариями."""
    post = get_object_or_404(
        NewsPost.objects.select_related('author'),
        slug=slug,
        is_published=True,
    )
    comments = (
        post.comments.filter(is_published=True)
        .select_related('author')
        .order_by('-created_at')
    )
    form = CommentForm()

    return render(
        request,
        'news/detail.html',
        {
            'post': post,
            'comments': comments,
            'form': form,
        },
    )


@login_required
@require_POST
def add_comment(request, slug):
    """Добавить комментарий к новости через HTMX.

    Возвращает HTML-фрагмент (partial) с обновлённым списком
    комментариев и пустой формой.
    """
    post = get_object_or_404(NewsPost, slug=slug, is_published=True)
    form = CommentForm(request.POST)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()

        comments = (
            post.comments.filter(is_published=True)
            .select_related('author')
            .order_by('-created_at')
        )
        form = CommentForm()  # пустая форма после успеха
    else:
        # При ошибке — возвращаем форму с ошибками,
        # но список комментариев тоже нужен (для замены)
        comments = (
            post.comments.filter(is_published=True)
            .select_related('author')
            .order_by('-created_at')
        )

    context = {
        'post': post,
        'comments': comments,
        'form': form,
    }

    html = render_to_string(
        'news/partials/comment_section.html',
        context,
        request=request,
    )
    return HttpResponse(html)


def stats_players(request):
    """Страница статистики игроков."""
    players = get_player_stats()
    return render(
        request,
        'stats/players.html',
        {'players': players},
    )


def stats_team(request):
    """Страница статистики команды."""
    stats = get_team_stats()
    return render(
        request,
        'stats/team.html',
        {'stats': stats},
    )


def gallery_list(request):
    """Список опубликованных альбомов."""
    albums = (
        Album.objects.filter(is_published=True)
        .annotate(photos_count=Count('photos'))
        .select_related('match')
        .order_by('-date', 'order')
    )
    return render(
        request,
        'gallery/list.html',
        {'albums': albums},
    )


def album_detail(request, slug):
    """Альбом с фотографиями."""
    album = get_object_or_404(
        Album.objects.prefetch_related('photos').select_related('match'),
        slug=slug,
        is_published=True,
    )
    photos = album.photos.order_by('order', 'id')
    return render(
        request,
        'gallery/detail.html',
        {'album': album, 'photos': photos},
    )


def staff_list(request):
    """Страница тренерского и административного состава."""
    staff = Staff.objects.filter(is_active=True).order_by('order', 'last_name')
    return render(
        request,
        'staff/list.html',
        {'staff': staff},
    )
