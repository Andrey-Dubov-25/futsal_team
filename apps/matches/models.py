from django.db import models

from config import constants as c


class Match(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = 'SCH', 'Запланирован'
        FINISHED = 'FIN', 'Завершён'
        CANCELLED = 'CAN', 'Отменён'

    opponent = models.CharField(
        'Соперник', max_length=c.MATCH_OPPONENT_MAX_LENGTH
    )
    opponent_logo = models.ImageField(
        'Логотип соперника', upload_to='opponents/', blank=True, null=True
    )
    date = models.DateTimeField('Дата и время')
    location = models.CharField(
        'Место', max_length=c.MATCH_LOCATION_MAX_LENGTH
    )
    is_home = models.BooleanField('Домашний матч', default=True)
    status = models.CharField(
        'Статус',
        max_length=c.MATCH_STATUS_MAX_LENGTH,
        choices=Status.choices,
        default=Status.SCHEDULED,
    )
    our_score = models.PositiveSmallIntegerField(
        'Наши голы', null=True, blank=True
    )
    opponent_score = models.PositiveSmallIntegerField(
        'Голы соперника', null=True, blank=True
    )
    comment = models.TextField('Комментарий', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Матч'
        verbose_name_plural = 'Матчи'
        ordering = ['-date']

    def __str__(self):
        return f'{self.opponent} — {self.date:%d.%m.%Y}'


class MatchEvent(models.Model):
    class EventType(models.TextChoices):
        GOAL = 'GOAL', 'Гол'
        ASSIST = 'ASSIST', 'Передача'
        YELLOW = 'YELLOW', 'Жёлтая карточка'
        RED = 'RED', 'Красная карточка'
        OWN_GOAL = 'OWN', 'Автогол'

    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name='events',
        verbose_name='Матч',
    )
    player = models.ForeignKey(
        'players.Player',
        on_delete=models.CASCADE,
        related_name='events',
        verbose_name='Игрок',
    )
    event_type = models.CharField(
        'Событие',
        max_length=c.MATCH_EVENT_TYPE_MAX_LENGTH,
        choices=EventType.choices,
    )
    minute = models.PositiveSmallIntegerField('Минута')

    class Meta:
        verbose_name = 'Событие матча'
        verbose_name_plural = 'События матча'
        ordering = ['minute']

    def __str__(self):
        return (
            f'{self.match} — {self.player} — '
            f'{self.get_event_type_display()} ({self.minute}")'
        )
