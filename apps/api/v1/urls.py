"""Маршруты API v1."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import MatchViewSet, NewsPostViewSet, PlayerViewSet


router = DefaultRouter()
router.register('players', PlayerViewSet, basename='player')
router.register('matches', MatchViewSet, basename='match')
router.register('news', NewsPostViewSet, basename='news')

urlpatterns = [
    path('', include(router.urls)),
]
