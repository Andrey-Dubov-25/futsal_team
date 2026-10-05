from django.db import models
from django.utils.text import slugify

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
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)
