"""URL-маршруты веб-сайта."""

from django.urls import path

from . import views


app_name = 'web'

urlpatterns = [
    path('', views.home, name='home'),
    path('players/', views.players_list, name='players-list'),
    path(
        'players/<int:pk>/',
        views.player_detail,
        name='player-detail',
    ),
    path('matches/', views.matches_list, name='matches-list'),
    path(
        'matches/<int:pk>/',
        views.match_detail,
        name='match-detail',
    ),
    path('news/', views.news_list, name='news-list'),
    path(
        'news/<slug:slug>/',
        views.news_detail,
        name='news-detail',
    ),
    path(
        'news/<slug:slug>/comment/',
        views.add_comment,
        name='news-add-comment',
    ),
    path('stats/', views.stats_team, name='stats-team'),
    path(
        'stats/players/',
        views.stats_players,
        name='stats-players',
    ),
]
