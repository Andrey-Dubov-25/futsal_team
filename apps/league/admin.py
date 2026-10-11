"""Админка для данных с befutsal.ru."""

from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from django.utils.html import format_html

from apps.league.models import BefutsalSnapshot, BefutsalTournament


# =============================================================================
# Снимок статистики
# =============================================================================


@admin.register(BefutsalSnapshot)
class BefutsalSnapshotAdmin(admin.ModelAdmin):
    """Снимки общей статистики с Befutsal.

    Только чтение: снимки создаются автоматически командой
    sync_befutsal. Ручное редактирование может сломать историю.
    """

    list_display = (
        'fetched_at',
        'founded_year',
        'ranking_place',
        'total_matches',
        'win_rate_display',
        'goals_display',
    )
    list_filter = ('founded_year',)
    ordering = ('-fetched_at',)
    date_hierarchy = 'fetched_at'

    readonly_fields = (
        'fetched_at',
        'founded_year',
        'ranking_place',
        'total_matches',
        'total_won',
        'total_drawn',
        'total_lost',
        'total_goals_scored',
        'total_goals_conceded',
        'goal_difference_display',
        'win_rate_display',
    )

    fieldsets = (
        (
            'Метаданные',
            {
                'fields': ('fetched_at',),
            },
        ),
        (
            'Профиль клуба',
            {
                'fields': ('founded_year', 'ranking_place'),
            },
        ),
        (
            'Общая статистика',
            {
                'fields': (
                    'total_matches',
                    ('total_won', 'total_drawn', 'total_lost'),
                    ('total_goals_scored', 'total_goals_conceded'),
                    'goal_difference_display',
                    'win_rate_display',
                ),
            },
        ),
    )

    def has_add_permission(self, request):
        """Запретить ручное создание — только через sync."""
        return False

    def has_change_permission(self, request, obj=None):
        """Запретить редактирование."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Разрешить удаление — на случай отката."""
        return True

    @admin.display(description='Win rate')
    def win_rate_display(self, obj):
        """Процент побед."""
        return f'{obj.win_rate}%'

    @admin.display(description='Разница мячей')
    def goal_difference_display(self, obj):
        """Разница мячей."""
        diff = obj.goal_difference
        sign = '+' if diff > 0 else ''
        return f'{sign}{diff}'

    @admin.display(description='Мячи')
    def goals_display(self, obj):
        """Забито-пропущено."""
        return f'{obj.total_goals_scored}-{obj.total_goals_conceded}'


# =============================================================================
# Турниры
# =============================================================================


@admin.register(BefutsalTournament)
class BefutsalTournamentAdmin(admin.ModelAdmin):
    """Турниры команды (данные с Befutsal)."""

    list_display = (
        'order',
        'name',
        'matches',
        'record_display',
        'goals_display',
        'points_display',
        'place_display',
        'is_active',
    )
    list_display_links = ('order', 'name')
    list_editable = ('is_active',)
    list_filter = (
        'is_active',
        'season',
        'place',
    )
    search_fields = ('name', 'season', 'competition', 'external_id')
    ordering = ('order', '-id')
    list_per_page = 25

    readonly_fields = (
        'external_id',
        'befutsal_url_display',
        'updated_at',
        'goal_difference_display',
        'is_champion',
        'is_prize',
    )

    fieldsets = (
        (
            'Идентификация',
            {
                'fields': (
                    'name',
                    'external_id',
                    'befutsal_url_display',
                    ('season', 'competition'),
                ),
            },
        ),
        (
            'Статистика',
            {
                'fields': (
                    'matches',
                    ('won', 'drawn', 'lost'),
                    ('goals_scored', 'goals_conceded'),
                    'goal_difference_display',
                    ('points', 'percent'),
                    'place',
                    ('is_champion', 'is_prize'),
                ),
            },
        ),
        (
            'Отображение',
            {
                'fields': ('order', 'is_active', 'updated_at'),
            },
        ),
    )

    actions = ['mark_active', 'mark_inactive']

    @admin.display(description='В-Н-П')
    def record_display(self, obj):
        """Счётчик В-Н-П."""
        return f'{obj.won}-{obj.drawn}-{obj.lost}'

    @admin.display(description='Мячи')
    def goals_display(self, obj):
        """Забито-пропущено."""
        return f'{obj.goals_scored}-{obj.goals_conceded}'

    @admin.display(description='Очки')
    def points_display(self, obj):
        """Очки + процент."""
        if obj.percent:
            return f'{obj.points} ({obj.percent}%)'
        return str(obj.points)

    @admin.display(description='Место')
    def place_display(self, obj):
        """Место с медалькой для призёров."""
        if obj.place is None:
            return '—'
        medals = {1: '🥇', 2: '🥈', 3: '🥉'}
        medal = medals.get(obj.place, '')
        if medal:
            return f'{medal} {obj.place}'
        return str(obj.place)

    @admin.display(description='Ссылка на Befutsal')
    def befutsal_url_display(self, obj):
        """Кликабельная ссылка на страницу турнира."""
        if not obj.befutsal_url:
            return '—'
        return format_html(
            '<a href="{}" target="_blank" rel="noopener">{}</a>',
            obj.befutsal_url,
            obj.befutsal_url,
        )

    @admin.display(boolean=True, description='Чемпион')
    def is_champion(self, obj):
        """Заняли 1-е место?"""
        return obj.is_champion

    @admin.display(boolean=True, description='Призёр')
    def is_prize(self, obj):
        """Заняли 1-3 место?"""
        return obj.is_prize

    @admin.display(description='Разница мячей')
    def goal_difference_display(self, obj):
        """Разница мячей."""
        diff = obj.goal_difference
        sign = '+' if diff > 0 else ''
        return f'{sign}{diff}'

    @admin.action(description='Пометить активными')
    def mark_active(self, request, queryset):
        """Пометить выбранные турниры активными."""
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f'Помечено активными: {updated}',
            messages.SUCCESS,
        )

    @admin.action(description='Снять активность')
    def mark_inactive(self, request, queryset):
        """Снять флаг активного у выбранных."""
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f'Снят флаг активного у {updated}',
            messages.SUCCESS,
        )

    # --- Кнопка запуска sync прямо из списка ---

    def get_urls(self):
        """Добавить кастомный URL для запуска sync."""
        urls = super().get_urls()
        custom = [
            path(
                'run-sync/',
                self.admin_site.admin_view(self.run_sync_view),
                name='league_befutsaltournament_run_sync',
            ),
        ]
        return custom + urls

    def run_sync_view(self, request):
        """Запустить sync_befutsal и вернуться в список."""
        from io import StringIO

        from django.core.management import call_command

        output = StringIO()
        try:
            call_command('sync_befutsal', stdout=output)
            result = output.getvalue()
            self.message_user(
                request,
                f'Синхронизация завершена:\n{result}',
                messages.SUCCESS,
            )
        except Exception as exc:
            self.message_user(
                request,
                f'Ошибка синхронизации: {exc}',
                messages.ERROR,
            )

        return HttpResponseRedirect(
            reverse('admin:league_befutsaltournament_changelist'),
        )

    def changelist_view(self, request, extra_context=None):
        """Добавить кнопку «Запустить sync» в шаблон списка."""
        extra_context = extra_context or {}
        extra_context['run_sync_url'] = reverse(
            'admin:league_befutsaltournament_run_sync',
        )
        return super().changelist_view(request, extra_context)
