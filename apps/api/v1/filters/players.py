"""Фильтры для игроков."""

import django_filters as filters

from apps.players.models import Player


class PlayerFilter(filters.FilterSet):
    """Фильтр игроков: позиция, активность, диапазон дат рождения, номер."""

    position = filters.ChoiceFilter(choices=Player.Position.choices)
    is_active = filters.BooleanFilter()
    number = filters.NumberFilter()
    birth_date_from = filters.DateFilter(
        field_name='birth_date',
        lookup_expr='gte',
    )
    birth_date_to = filters.DateFilter(
        field_name='birth_date',
        lookup_expr='lte',
    )

    class Meta:
        model = Player
        fields = ['position', 'is_active', 'number']
