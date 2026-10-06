"""Сериализаторы тренерского состава."""

from rest_framework import serializers

from apps.staff.models import Staff


class StaffSerializer(serializers.ModelSerializer):
    """Сериализатор сотрудника."""

    full_name = serializers.CharField(read_only=True)
    role_display = serializers.CharField(
        source='get_role_display',
        read_only=True,
    )

    class Meta:
        model = Staff
        fields = [
            'id',
            'first_name',
            'last_name',
            'full_name',
            'role',
            'role_display',
            'photo',
            'bio',
            'phone',
            'email',
            'order',
            'is_active',
        ]
