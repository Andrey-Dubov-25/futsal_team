"""Сериализаторы игроков."""

from rest_framework import serializers

from apps.players.models import Player


class PlayerSerializer(serializers.ModelSerializer):
    """Сериализатор игрока для чтения и записи."""

    full_name = serializers.SerializerMethodField()
    position_display = serializers.CharField(
        source='get_position_display', read_only=True
    )

    class Meta:
        model = Player
        fields = [
            'id',
            'first_name',
            'last_name',
            'nickname',
            'full_name',
            'number',
            'position',
            'position_display',
            'birth_date',
            'photo',
            'bio',
            'is_active',
        ]

    def get_full_name(self, obj):
        return f'{obj.last_name} {obj.first_name}'
