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
]
