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
