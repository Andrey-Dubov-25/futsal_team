"""Сериализаторы матчей и событий матча."""

from rest_framework import serializers

from apps.matches.models import Match, MatchEvent
from apps.players.models import Player

from .players import PlayerSerializer


class MatchEventSerializer(serializers.ModelSerializer):
    """Сериализатор события матча (гол, карточка и т.п.)."""

    player = PlayerSerializer(read_only=True)
    player_id = serializers.PrimaryKeyRelatedField(
        queryset=Player.objects.all(),
        source='player',
        write_only=True,
    )
    event_type_display = serializers.CharField(
        source='get_event_type_display', read_only=True
    )

    class Meta:
        model = MatchEvent
        fields = [
            'id',
            'player',
            'player_id',
            'event_type',
            'event_type_display',
            'minute',
        ]


class MatchSerializer(serializers.ModelSerializer):
    """Сериализатор матча вместе с вложенными событиями и результатом."""

    events = MatchEventSerializer(many=True, read_only=True)
    status_display = serializers.CharField(
        source='get_status_display', read_only=True
    )
    result = serializers.SerializerMethodField()

    class Meta:
        model = Match
        fields = [
            'id',
            'opponent',
            'opponent_logo',
            'date',
            'location',
            'is_home',
            'status',
            'status_display',
            'our_score',
            'opponent_score',
            'result',
            'comment',
            'events',
        ]

    def get_result(self, obj):
        if obj.status != Match.Status.FINISHED:
            return None
        if obj.our_score > obj.opponent_score:
            return 'W'
        if obj.our_score < obj.opponent_score:
            return 'L'
        return 'D'
