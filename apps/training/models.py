"""Модели тренировок."""

from django.db import models

from config import constants as c


class Training(models.Model):
    """Разовая тренировка в расписании."""

    title = models.CharField(
        'Название',
        max_length=c.TRAINING_TITLE_MAX_LENGTH,
    )
    date = models.DateTimeField('Дата и время')
    duration_minutes = models.PositiveSmallIntegerField(
        'Длительность (мин)',
        default=c.TRAINING_DEFAULT_DURATION_MINUTES,
    )
    location = models.CharField(
        'Место',
        max_length=c.TRAINING_LOCATION_MAX_LENGTH,
    )
    coach = models.ForeignKey(
        'staff.Staff',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='trainings',
        verbose_name='Тренер',
    )
    is_cancelled = models.BooleanField('Отменена', default=False)
    comment = models.TextField('Комментарий', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Тренировка'
        verbose_name_plural = 'Тренировки'
        ordering = ['-date']

    def __str__(self):
        return f'{self.title} — {self.date:%d.%m.%Y %H:%M}'
