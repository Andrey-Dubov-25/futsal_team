"""Сериализаторы тренировок."""

from rest_framework import serializers

from apps.staff.models import Staff
from apps.training.models import Training

from .staff import StaffSerializer


class TrainingSerializer(serializers.ModelSerializer):
    """Сериализатор тренировки."""

    coach = StaffSerializer(read_only=True)
    coach_id = serializers.PrimaryKeyRelatedField(
        queryset=Staff.objects.all(),
        source='coach',
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Training
        fields = [
            'id',
            'title',
            'date',
            'duration_minutes',
            'location',
            'coach',
            'coach_id',
            'is_cancelled',
            'comment',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']
