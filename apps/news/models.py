from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from unidecode import unidecode

from config import constants as c


class NewsPost(models.Model):
    """Новость команды — своя или из ВК."""

    class Source(models.TextChoices):
        SITE = 'SITE', 'С сайта'
        VK = 'VK', 'ВКонтакте'

    title = models.CharField(
        'Заголовок',
        max_length=c.NEWS_TITLE_MAX_LENGTH,
    )
    slug = models.SlugField(
        'Слаг',
        max_length=c.NEWS_SLUG_MAX_LENGTH,
        unique=True,
        blank=True,
    )
    cover = models.ImageField(
        'Обложка',
        upload_to='news/',
        blank=True,
        null=True,
    )
    excerpt = models.CharField(
        'Краткое описание',
        max_length=c.NEWS_EXCERPT_MAX_LENGTH,
        blank=True,
    )
    content = models.TextField('Текст')
    author = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='news_posts',
        verbose_name='Автор',
    )
    is_published = models.BooleanField('Опубликовано', default=True)

    # --- Источник (для ВК-постов) ---
    source = models.CharField(
        'Источник',
        max_length=10,
        choices=Source.choices,
        default=Source.SITE,
    )
    external_id = models.CharField(
        'ID поста во ВКонтакте',
        max_length=c.VK_EXTERNAL_ID_MAX_LENGTH,
        unique=True,
        null=True,
        blank=True,
        help_text='Формат: <owner_id>_<post_id>, например -230450774_330',
    )
    external_url = models.URLField(
        'Ссылка на источник',
        blank=True,
        help_text='Прямая ссылка на пост в ВК',
    )
    has_video = models.BooleanField(
        'Содержит видео',
        default=False,
        help_text='Если True — показываем кнопку «Смотреть видео в ВК»',
    )

    published_at = models.DateTimeField(
        'Дата публикации',
        default=timezone.now,
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ['-published_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """Сгенерировать ASCII-slug из заголовка при первом сохранении.

        Если slug занят — добавляем числовой суффикс (-2, -3, ...).
        """
        if not self.slug:
            transliterated = unidecode(self.title)
            base_slug = slugify(transliterated) or f'news-{self.pk or "new"}'

            self.slug = base_slug

            # Уникализация
            counter = 1
            while (
                NewsPost.objects.exclude(pk=self.pk)
                .filter(slug=self.slug)
                .exists()
            ):
                counter += 1
                self.slug = f'{base_slug}-{counter}'

        super().save(*args, **kwargs)

    @property
    def is_from_vk(self):
        """Новость загружена из ВК."""
        return self.source == self.Source.VK

    @property
    def is_from_site(self):
        """Новость создана вручную."""
        return self.source == self.Source.SITE


class Comment(models.Model):
    """Комментарий к новости."""

    post = models.ForeignKey(
        NewsPost,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Новость',
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор',
    )
    text = models.TextField(
        'Текст',
        max_length=c.COMMENT_TEXT_MAX_LENGTH,
    )
    is_published = models.BooleanField(
        'Опубликован',
        default=True,
    )
    created_at = models.DateTimeField(
        'Дата создания',
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        'Дата обновления',
        auto_now=True,
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['post', 'is_published']),
        ]

    def __str__(self):
        return f'{self.author} → {self.post}: {self.text[:30]}'
