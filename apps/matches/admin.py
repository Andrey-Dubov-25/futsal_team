# Register your models here.
from django.contrib import admin

from .models import Match, MatchEvent


class MatchEventInline(admin.TabularInline):
    """Инлайн событий матча (голы, карточки)."""

    model = MatchEvent
    extra = 1
    fields = ('player', 'event_type', 'minute')
    ordering = ('minute',)


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = (
        'opponent',
        'date',
        'is_home',
        'status',
        'our_score',
        'opponent_score',
    )
    list_filter = ('status', 'is_home', 'date')
    search_fields = ('opponent', 'location')
    date_hierarchy = 'date'
    raw_id_fields = ()
    inlines = [MatchEventInline]


@admin.register(MatchEvent)
class MatchEventAdmin(admin.ModelAdmin):
    list_display = ('match', 'player', 'event_type', 'minute')
    list_filter = ('event_type',)
    search_fields = ('player__last_name', 'match__opponent')
    raw_id_fields = ('match', 'player')
