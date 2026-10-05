from django.contrib.auth.models import AbstractUser
from django.db import models

from config import constants as c


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Администратор'
        COACH = 'COACH', 'Тренер'
        PLAYER = 'PLAYER', 'Игрок'
        FAN = 'FAN', 'Болельщик'

    role = models.CharField(
        'Роль',
        max_length=c.USER_ROLE_MAX_LENGTH,
        choices=Role.choices,
        default=Role.FAN,
    )
    phone = models.CharField(
        'Телефон', max_length=c.USER_PHONE_MAX_LENGTH, blank=True
    )
    avatar = models.ImageField(
        'Аватар', upload_to='avatars/', blank=True, null=True
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
