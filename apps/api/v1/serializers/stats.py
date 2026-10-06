"""Сериализаторы статистики."""

from rest_framework import serializers


class PlayerStatsSerializer(serializers.Serializer):
    """Статистика игрока: голы, передачи, карточки."""

    id = serializers.IntegerField()
    full_name = serializers.CharField()
    number = serializers.IntegerField(allow_null=True)
    position = serializers.CharField()
    position_display = serializers.CharField()
    goals = serializers.IntegerField()
    assists = serializers.IntegerField()
    yellow_cards = serializers.IntegerField()
    red_cards = serializers.IntegerField()
    matches_played = serializers.IntegerField()
    points = serializers.IntegerField()


class TeamStatsSerializer(serializers.Serializer):
    """Общая статистика команды."""

    matches_total = serializers.IntegerField()
    matches_won = serializers.IntegerField()
    matches_drawn = serializers.IntegerField()
    matches_lost = serializers.IntegerField()
    goals_scored = serializers.IntegerField()
    goals_conceded = serializers.IntegerField()
    goal_difference = serializers.IntegerField()
    avg_goals_scored = serializers.FloatField()
    avg_goals_conceded = serializers.FloatField()
    win_rate = serializers.FloatField()
    form = serializers.ListField(child=serializers.CharField())
