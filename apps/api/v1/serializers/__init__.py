"""Сериализаторы API v1."""

from .auth import (
    RegisterSerializer,
    UpdateProfileSerializer,
    UserSerializer,
)
from .comments import CommentCreateSerializer, CommentSerializer
from .matches import MatchEventSerializer, MatchSerializer
from .news import NewsPostSerializer
from .players import PlayerSerializer
from .staff import StaffSerializer
from .stats import PlayerStatsSerializer, TeamStatsSerializer
from .training import TrainingSerializer


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
    'CommentSerializer',
    'CommentCreateSerializer',
    'StaffSerializer',
    'TrainingSerializer',
]
