"""Модели фотогалереи."""

from django.db import models
from django.utils.text import slugify
from unidecode import unidecode

from config import constants as c


class Album(models.Model):
    """Альбом с фотографиями — например, с матча или турнира."""

    title = models.CharField(
        'Название',
        max_length=c.ALBUM_TITLE_MAX_LENGTH,
    )
    slug = models.SlugField(
        'Слаг',
        max_length=c.ALBUM_SLUG_MAX_LENGTH,
        unique=True,
        blank=True,
    )
    description = models.TextField(
        'Описание',
        max_length=c.ALBUM_DESCRIPTION_MAX_LENGTH,
        blank=True,
    )
    cover = models.ImageField(
        'Обложка',
        upload_to='gallery/covers/',
        blank=True,
        null=True,
    )
    date = models.DateField('Дата события')
    match = models.ForeignKey(
        'matches.Match',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='albums',
        verbose_name='Матч',
    )
    is_published = models.BooleanField('Опубликован', default=True)
    order = models.PositiveSmallIntegerField(
        'Порядок',
        default=100,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Альбом'
        verbose_name_plural = 'Фотоальбомы'
        ordering = ['-date', 'order']

    def __str__(self):
        return f'{self.title} ({self.date:%d.%m.%Y})'

    def save(self, *args, **kwargs):
        """Сгенерировать ASCII-slug из заголовка при первом сохранении."""
        if not self.slug:
            transliterated = unidecode(self.title)
            self.slug = slugify(transliterated)
            if not self.slug:
                self.slug = f'album-{self.pk or "new"}'
        super().save(*args, **kwargs)


class Photo(models.Model):
    """Фотография внутри альбома."""

    album = models.ForeignKey(
        Album,
        on_delete=models.CASCADE,
        related_name='photos',
        verbose_name='Альбом',
    )
    image = models.ImageField(
        'Фото',
        upload_to='gallery/photos/',
    )
    caption = models.CharField(
        'Подпись',
        max_length=c.PHOTO_CAPTION_MAX_LENGTH,
        blank=True,
    )
    order = models.PositiveSmallIntegerField('Порядок', default=100)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Фотография'
        verbose_name_plural = 'Фотографии'
        ordering = ['order', 'id']

    def __str__(self):
        return self.caption or f'Фото #{self.pk} из «{self.album.title}»'
