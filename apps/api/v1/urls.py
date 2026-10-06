"""Маршруты API v1."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AlbumViewSet,
    CommentViewSet,
    LogoutView,
    MatchViewSet,
    MeView,
    NewsPostViewSet,
    PhotoViewSet,
    PlayerStatsViewSet,
    PlayerViewSet,
    RegisterView,
    StaffViewSet,
    TeamStatsViewSet,
    TrainingViewSet,
)


router = DefaultRouter()
router.register('players', PlayerViewSet, basename='player')
router.register('matches', MatchViewSet, basename='match')
router.register('news', NewsPostViewSet, basename='news')
router.register('comments', CommentViewSet, basename='comment')
router.register('staff', StaffViewSet, basename='staff')
router.register('trainings', TrainingViewSet, basename='training')
router.register('albums', AlbumViewSet, basename='album')
router.register('photos', PhotoViewSet, basename='photo')
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
