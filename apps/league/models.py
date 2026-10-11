"""Модели данных с сайта Лиги (befutsal.ru)."""

from django.db import models

from config import constants as c


class BefutsalSnapshot(models.Model):
    """Снимок общей статистики команды с Befutsal.

    Храним историю снимков — если Лига исправит цифры или
    добавит новый турнир, у нас будет эволюция показателей.
    """

    fetched_at = models.DateTimeField(
        'Дата снимка',
        auto_now_add=True,
    )

    # Профиль клуба
    founded_year = models.PositiveSmallIntegerField(
        'Год основания',
        null=True,
        blank=True,
    )
    ranking_place = models.PositiveSmallIntegerField(
        'Место в рейтинге befutsal',
        null=True,
        blank=True,
    )

    # Общая статистика за всё время
    total_matches = models.PositiveIntegerField('Всего игр', default=0)
    total_won = models.PositiveIntegerField('Побед', default=0)
    total_drawn = models.PositiveIntegerField('Ничьих', default=0)
    total_lost = models.PositiveIntegerField('Поражений', default=0)
    total_goals_scored = models.PositiveIntegerField('Забито', default=0)
    total_goals_conceded = models.PositiveIntegerField(
        'Пропущено',
        default=0,
    )

    class Meta:
        verbose_name = 'Снимок с Befutsal'
        verbose_name_plural = 'Снимки с Befutsal'
        ordering = ['-fetched_at']

    def __str__(self):
        return f'Снимок от {self.fetched_at:%d.%m.%Y %H:%M}'

    @property
    def goal_difference(self):
        """Разница мячей."""
        return self.total_goals_scored - self.total_goals_conceded

    @property
    def win_rate(self):
        """Процент побед."""
        if not self.total_matches:
            return 0
        return round(self.total_won / self.total_matches * 100, 1)


class BefutsalTournament(models.Model):
    """Турнир, в котором участвовала команда (данные с Befutsal).

    Синхронизируется автоматически: старые записи обновляются,
    новые добавляются. По `external_id` отличаем турниры.
    """

    external_id = models.CharField(
        'ID турнира на Befutsal',
        max_length=c.BEFUTSAL_EXTERNAL_ID_MAX_LENGTH,
        unique=True,
        null=True,
        blank=True,
        default=None,
        help_text='Параметр l из URL league.php?l=...',
    )
    name = models.CharField(
        'Название турнира',
        max_length=c.BEFUTSAL_TOURNAMENT_NAME_MAX_LENGTH,
    )
    season = models.CharField(
        'Сезон',
        max_length=c.BEFUTSAL_SEASON_MAX_LENGTH,
        blank=True,
        help_text='Например: Лето 2026',
    )
    competition = models.CharField(
        'Соревнование',
        max_length=c.BEFUTSAL_COMPETITION_MAX_LENGTH,
        blank=True,
        help_text='Например: 4-я лига. Зона Б',
    )

    # Статистика в турнире
    matches = models.PositiveSmallIntegerField('Игр', default=0)
    won = models.PositiveSmallIntegerField('Побед', default=0)
    drawn = models.PositiveSmallIntegerField('Ничьих', default=0)
    lost = models.PositiveSmallIntegerField('Поражений', default=0)
    goals_scored = models.PositiveSmallIntegerField('Забито', default=0)
    goals_conceded = models.PositiveSmallIntegerField(
        'Пропущено',
        default=0,
    )
    points = models.PositiveSmallIntegerField('Очков', default=0)
    percent = models.PositiveSmallIntegerField(
        'Процент очков',
        null=True,
        blank=True,
        help_text='Из скобок, например 84 из "38(84%)"',
    )
    place = models.PositiveSmallIntegerField(
        'Место',
        null=True,
        blank=True,
        help_text='Пусто для кубковых турниров',
    )

    # Мета
    order = models.PositiveSmallIntegerField(
        'Порядок',
        default=0,
        help_text='Порядок как на Befutsal (сверху — свежие)',
    )
    is_active = models.BooleanField(
        'Активный',
        default=False,
        help_text='Текущий сезон — выделяется на сайте',
    )
    is_active = models.BooleanField(
        'Активный',
        default=False,
        help_text='Текущий сезон — выделяется на сайте',
    )
    is_pinned = models.BooleanField(
        'Закреплён вручную',
        default=False,
        help_text=(
            'Если True — sync_befutsal не перезаписывает is_active. '
            'Используй для скоротечных турниров, чтобы переместить '
            'их вручную в прошедшие.'
        ),
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Турнир (Befutsal)'
        verbose_name_plural = 'Турниры (Befutsal)'
        ordering = ['order', '-id']

    def __str__(self):
        return self.name

    @property
    def goal_difference(self):
        """Разница мячей."""
        return self.goals_scored - self.goals_conceded

    @property
    def is_champion(self):
        """Заняли 1-е место."""
        return self.place == 1

    @property
    def is_prize(self):
        """Заняли 1-3 места."""
        return self.place is not None and 1 <= self.place <= 3

    @property
    def befutsal_url(self):
        """Ссылка на страницу турнира на Befutsal. None, если нет ID."""
        if not self.external_id:
            return None
        return f'{c.BEFUTSAL_BASE_URL}/league.php?l={self.external_id}'
