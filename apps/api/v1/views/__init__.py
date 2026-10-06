"""ViewSet'ы API v1."""

from .auth import LogoutView, MeView, RegisterView
from .comments import CommentViewSet
from .matches import MatchViewSet
from .news import NewsPostViewSet
from .players import PlayerViewSet
from .staff import StaffViewSet
from .stats import PlayerStatsViewSet, TeamStatsViewSet
from .training import TrainingViewSet


__all__ = [
    'PlayerViewSet',
    'MatchViewSet',
    'NewsPostViewSet',
    'PlayerStatsViewSet',
    'TeamStatsViewSet',
    'RegisterView',
    'MeView',
    'LogoutView',
    'CommentViewSet',
    'StaffViewSet',
    'TrainingViewSet',
]
