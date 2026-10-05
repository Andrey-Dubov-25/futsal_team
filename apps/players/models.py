from django.db import models

from config import constants as c


class Player(models.Model):
    class Position(models.TextChoices):
        GOALKEEPER = 'GK', 'Вратарь'
        DEFENDER = 'DF', 'Защитник'
        WINGER = 'WG', 'Крайний'
        FORWARD = 'FW', 'Нападающий'

    user = models.OneToOneField(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='player_profile',
        verbose_name='Аккаунт',
    )
    first_name = models.CharField(
        'Имя', max_length=c.PLAYER_FIRST_NAME_MAX_LENGTH
    )
    last_name = models.CharField(
        'Фамилия', max_length=c.PLAYER_LAST_NAME_MAX_LENGTH
    )
    nickname = models.CharField(
        'Прозвище', max_length=c.PLAYER_NICKNAME_MAX_LENGTH, blank=True
    )
    number = models.PositiveSmallIntegerField(
        'Номер', unique=True, null=True, blank=True
    )
    position = models.CharField(
        'Позиция',
        max_length=c.PLAYER_POSITION_MAX_LENGTH,
        choices=Position.choices,
    )
    birth_date = models.DateField('Дата рождения', null=True, blank=True)
    photo = models.ImageField(
        'Фото', upload_to='players/', blank=True, null=True
    )
    bio = models.TextField('О команде', blank=True)
    is_active = models.BooleanField('В команде', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Игрок'
        verbose_name_plural = 'Игроки'
        ordering = ['number']

    def __str__(self):
        return f'#{self.number or "—"} {self.last_name} {self.first_name}'
