"""ViewSet'ы API v1."""

from .matches import MatchViewSet
from .news import NewsPostViewSet
from .players import PlayerViewSet


__all__ = [
    'PlayerViewSet',
    'MatchViewSet',
    'NewsPostViewSet',
]
