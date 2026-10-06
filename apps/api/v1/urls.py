"""Маршруты API v1."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    MatchViewSet,
    NewsPostViewSet,
    PlayerStatsViewSet,
    PlayerViewSet,
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
    path('', include(router.urls)),
]
