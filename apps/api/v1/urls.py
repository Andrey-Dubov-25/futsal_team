"""Маршруты API v1."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    LogoutView,
    MatchViewSet,
    MeView,
    NewsPostViewSet,
    PlayerStatsViewSet,
    PlayerViewSet,
    RegisterView,
    TeamStatsViewSet,
)


router = DefaultRouter()
router.register('players', PlayerViewSet, basename='player')
router.register('matches', MatchViewSet, basename='match')
router.register('news', NewsPostViewSet, basename='news')
router.register(
    'stats/players',
    PlayerStatsViewSet,
    basename='stats-players',
)
router.register(
    'stats/team',
    TeamStatsViewSet,
    basename='stats-team',
)

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='auth-register'),
    path('auth/me/', MeView.as_view(), name='auth-me'),
    path('auth/logout/', LogoutView.as_view(), name='auth-logout'),
    path('', include(router.urls)),
]
