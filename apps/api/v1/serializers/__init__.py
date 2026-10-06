"""Сериализаторы API v1."""

from .auth import (
    RegisterSerializer,
    UpdateProfileSerializer,
    UserSerializer,
)
from .matches import MatchEventSerializer, MatchSerializer
from .news import NewsPostSerializer
from .players import PlayerSerializer
from .stats import PlayerStatsSerializer, TeamStatsSerializer


__all__ = [
    'PlayerSerializer',
    'MatchSerializer',
    'MatchEventSerializer',
    'NewsPostSerializer',
    'PlayerStatsSerializer',
    'TeamStatsSerializer',
    'UserSerializer',
    'RegisterSerializer',
    'UpdateProfileSerializer',
]
