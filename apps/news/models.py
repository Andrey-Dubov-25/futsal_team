from django.conf import settings
from django.db import models
from django.utils.text import slugify
from unidecode import unidecode

from config import constants as c


class NewsPost(models.Model):
    title = models.CharField('Заголовок', max_length=c.NEWS_TITLE_MAX_LENGTH)
    slug = models.SlugField(
        'Слаг',
        max_length=c.NEWS_SLUG_MAX_LENGTH,
        unique=True,
        blank=True,
    )
    cover = models.ImageField(
        'Обложка', upload_to='news/', blank=True, null=True
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
    published_at = models.DateTimeField('Дата публикации', auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ['-published_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """Сгенерировать ASCII-slug из заголовка при первом сохранении."""
        if not self.slug:
            transliterated = unidecode(self.title)
            self.slug = slugify(transliterated)
            # если получился пустой (например, только эмодзи) — fallback
            if not self.slug:
                self.slug = f'news-{self.pk or "new"}'
        super().save(*args, **kwargs)


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
