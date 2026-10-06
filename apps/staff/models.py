"""Модели тренерского и административного состава."""

from django.conf import settings
from django.db import models

from config import constants as c


class Staff(models.Model):
    """Член тренерского или административного состава."""

    class Role(models.TextChoices):
        HEAD_COACH = 'HEAD_COACH', 'Главный тренер'
        ASSISTANT = 'ASSISTANT', 'Ассистент'
        DOCTOR = 'DOCTOR', 'Врач'
        ADMIN = 'ADMIN', 'Администратор'
        OTHER = 'OTHER', 'Другое'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='staff_profile',
        verbose_name='Аккаунт',
    )
    first_name = models.CharField(
        'Имя', max_length=c.STAFF_FIRST_NAME_MAX_LENGTH
    )
    last_name = models.CharField(
        'Фамилия', max_length=c.STAFF_LAST_NAME_MAX_LENGTH
    )
    role = models.CharField(
        'Должность',
        max_length=c.STAFF_ROLE_MAX_LENGTH,
        choices=Role.choices,
    )
    photo = models.ImageField(
        'Фото',
        upload_to='staff/',
        blank=True,
        null=True,
    )
    bio = models.TextField('О человеке', blank=True)
    phone = models.CharField(
        'Телефон',
        max_length=c.STAFF_PHONE_MAX_LENGTH,
        blank=True,
    )
    email = models.EmailField(
        'Email',
        max_length=c.STAFF_EMAIL_MAX_LENGTH,
        blank=True,
    )
    order = models.PositiveSmallIntegerField(
        'Порядок отображения',
        default=100,
    )
    is_active = models.BooleanField('Работает', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Тренерский состав'
        ordering = ['order', 'last_name', 'first_name']

    def __str__(self):
        return (
            f'{self.last_name} {self.first_name} — {self.get_role_display()}'
        )

    @property
    def full_name(self):
        """Полное имя одной строкой."""
        return f'{self.last_name} {self.first_name}'
