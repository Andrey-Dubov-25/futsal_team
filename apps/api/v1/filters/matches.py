"""Фильтры для матчей."""

import django_filters as filters

from apps.matches.models import Match


class MatchFilter(filters.FilterSet):
    """Фильтр матчей: статус, домашний/гостевой, диапазон дат."""

    status = filters.ChoiceFilter(choices=Match.Status.choices)
    is_home = filters.BooleanFilter()
    date_from = filters.DateTimeFilter(
        field_name='date',
        lookup_expr='gte',
    )
    date_to = filters.DateTimeFilter(
        field_name='date',
        lookup_expr='lte',
    )

    class Meta:
        model = Match
        fields = ['status', 'is_home']
