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
    path('staff/', views.staff_list, name='staff-list'),
    path('trainings/', views.trainings_list, name='trainings-list'),
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
    path('gallery/', views.gallery_list, name='gallery-list'),
    path(
        'gallery/<slug:slug>/',
        views.album_detail,
        name='album-detail',
    ),
    path('stats/', views.stats_team, name='stats-team'),
    path(
        'stats/players/',
        views.stats_players,
        name='stats-players',
    ),
]
