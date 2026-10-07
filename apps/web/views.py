"""View-функции для HTML-страниц."""

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.gallery.models import Album
from apps.matches.models import Match
from apps.news.models import NewsPost
from apps.players.models import Player
from apps.staff.models import Staff
from apps.training.models import Training
from config import constants as c

from .forms import CommentForm, LoginForm, RegisterForm
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
    """Список матчей: ближайшие и прошедшие (с пагинацией)."""
    now = timezone.now()

    upcoming = Match.objects.filter(
        date__gte=now, status=Match.Status.SCHEDULED
    ).order_by('date')

    results_qs = Match.objects.filter(status=Match.Status.FINISHED).order_by(
        '-date'
    )

    paginator = Paginator(results_qs, c.PAGE_SIZE_MATCHES)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        'matches/list.html',
        {
            'upcoming': upcoming,
            'results': page_obj,  # список результатов — постранично
            'page_obj': page_obj,
            'is_paginated': page_obj.has_other_pages(),
        },
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
    """Список опубликованных новостей с пагинацией."""
    news = (
        NewsPost.objects.filter(is_published=True)
        .select_related('author')
        .order_by('-published_at')
    )

    paginator = Paginator(news, c.PAGE_SIZE_NEWS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        'news/list.html',
        {
            'news': page_obj,
            'page_obj': page_obj,
            'is_paginated': page_obj.has_other_pages(),
        },
    )


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
    """Список опубликованных альбомов с пагинацией."""
    albums = (
        Album.objects.filter(is_published=True)
        .annotate(photos_count=Count('photos'))
        .select_related('match')
        .order_by('-date', 'order')
    )

    paginator = Paginator(albums, c.PAGE_SIZE_GALLERY)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        'gallery/list.html',
        {
            'albums': page_obj,
            'page_obj': page_obj,
            'is_paginated': page_obj.has_other_pages(),
        },
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


def trainings_list(request):
    """Страница расписания тренировок."""
    now = timezone.now()

    upcoming = (
        Training.objects.filter(date__gte=now, is_cancelled=False)
        .select_related('coach')
        .order_by('date')
    )
    past = (
        Training.objects.filter(date__lt=now)
        .select_related('coach')
        .order_by('-date')[:20]
    )

    return render(
        request,
        'training/list.html',
        {'upcoming': upcoming, 'past': past},
    )


class WebLoginView(LoginView):
    """Страница входа."""

    template_name = 'auth/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True


class WebLogoutView(LogoutView):
    """Выход из системы. Редиректит на главную."""

    next_page = 'web:home'


def register_view(request):
    """Регистрация нового пользователя."""
    if request.user.is_authenticated:
        return redirect('web:home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                'Добро пожаловать! Аккаунт создан.',
            )
            return redirect('web:home')
    else:
        form = RegisterForm()

    return render(
        request,
        'auth/register.html',
        {'form': form},
    )


@login_required
def profile_view(request):
    """Профиль текущего пользователя."""
    return render(
        request,
        'auth/profile.html',
        {'profile_user': request.user},
    )


def handler404(request, exception):
    """Кастомная страница 404."""
    return render(request, '404.html', status=404)


def handler500(request):
    """Кастомная страница 500."""
    return render(request, '500.html', status=500)


def robots_txt(request):
    """Отдаёт файл robots.txt."""
    lines = [
        'User-agent: *',
        'Disallow: /admin/',
        'Disallow: /api/',
        '',
        f'Sitemap: {request.build_absolute_uri("/sitemap.xml")}',
    ]
    return HttpResponse(
        '\n'.join(lines),
        content_type='text/plain',
    )


def sitemap_xml(request):
    """Отдаёт простой XML-sitemap со всеми публичными URL."""
    urls = [
        reverse('web:home'),
        reverse('web:players-list'),
        reverse('web:staff-list'),
        reverse('web:trainings-list'),
        reverse('web:matches-list'),
        reverse('web:news-list'),
        reverse('web:stats-team'),
        reverse('web:stats-players'),
        reverse('web:gallery-list'),
    ]

    # Динамические страницы — новости и альбомы
    for post in NewsPost.objects.filter(is_published=True):
        urls.append(reverse('web:news-detail', args=[post.slug]))
    for album in Album.objects.filter(is_published=True):
        urls.append(reverse('web:album-detail', args=[album.slug]))

    base_url = request.build_absolute_uri('/').rstrip('/')
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for url in urls:
        lines.append('  <url>')
        lines.append(f'    <loc>{base_url}{url}</loc>')
        lines.append('  </url>')
    lines.append('</urlset>')

    return HttpResponse(
        '\n'.join(lines),
        content_type='application/xml',
    )
