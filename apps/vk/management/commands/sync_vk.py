"""Management command: синхронизация постов из ВКонтакте.

Использование:

    python manage.py sync_vk
    python manage.py sync_vk --dry-run
    python manage.py sync_vk --count=50

Что делает:
    1. Загружает последние посты со стены группы ВК.
    2. Создаёт/обновляет NewsPost с source='VK'.
    3. Пропускает посты без изменений.
    4. Логирует результат.
"""

import logging

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.news.models import NewsPost
from apps.vk.parser import VkParseError, parse_wall


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Синхронизировать посты из ВКонтакте'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Показать, что было бы сделано, без записи в БД',
        )
        parser.add_argument(
            '--count',
            type=int,
            default=None,
            help='Сколько постов загрузить (по умолчанию 30)',
        )
        parser.add_argument(
            '--skip-covers',
            action='store_true',
            help='Не скачивать обложки (только текст)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        count = options['count']
        skip_covers = options['skip_covers']

        self.stdout.write('Загрузка постов из ВК...')

        # --- Парсинг ---
        try:
            feed = parse_wall(count=count)
        except VkParseError as exc:
            self.stderr.write(
                self.style.ERROR(f'Ошибка парсинга: {exc}'),
            )
            return

        self.stdout.write(
            self.style.SUCCESS(
                f'Получено постов: {len(feed.posts)} '
                f'(всего в группе: {feed.total_count})',
            ),
        )

        if dry_run:
            self._show_dry_run(feed)
            return

        # --- Запись ---
        stats = {
            'created': 0,
            'updated': 0,
            'skipped': 0,
            'covers': 0,
        }

        with transaction.atomic():
            for post in feed.posts:
                result = self._sync_post(post, skip_covers)
                stats[result] += 1
                if result == 'created' and post.cover_url and not skip_covers:
                    stats['covers'] += 1

        # --- Итог ---
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('Синхронизация завершена'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(f'Создано:    {stats["created"]}')
        self.stdout.write(f'Обновлено:  {stats["updated"]}')
        self.stdout.write(f'Пропущено:  {stats["skipped"]}')
        if not skip_covers:
            self.stdout.write(f'Обложек:    {stats["covers"]}')

    def _sync_post(self, post, skip_covers):
        """Создать или обновить NewsPost. Вернуть статус."""
        existing = NewsPost.objects.filter(
            external_id=post.external_id,
        ).first()

        if existing:
            # Обновляем текст, если изменился
            changed = False
            if existing.content != post.content:
                existing.content = post.content
                existing.title = post.title
                existing.excerpt = post.excerpt
                changed = True
            if existing.has_video != post.has_video:
                existing.has_video = post.has_video
                changed = True

            if changed:
                existing.save(
                    update_fields=[
                        'content',
                        'title',
                        'excerpt',
                        'has_video',
                    ]
                )
                return 'updated'
            return 'skipped'

        # Создаём новый
        news = NewsPost(
            title=post.title,
            content=post.content,
            excerpt=post.excerpt,
            source=NewsPost.Source.VK,
            external_id=post.external_id,
            external_url=post.external_url,
            has_video=post.has_video,
            is_published=True,
        )
        news.published_at = post.published_at
        news.save()

        # Обложка — отдельным шагом (скачивание)
        if post.cover_url and not skip_covers:
            self._download_cover(news, post.cover_url)

        return 'created'

    def _download_cover(self, news, url):
        """Скачать обложку и прикрепить к новости."""
        try:
            import requests

            response = requests.get(url, timeout=15)
            response.raise_for_status()

            # Имя файла: vk_<post_id>.jpg
            filename = f'vk_{news.external_id.replace("-", "n")}.jpg'
            news.cover.save(
                filename,
                ContentFile(response.content),
                save=True,
            )
        except Exception as exc:
            logger.warning(
                'Не удалось скачать обложку для %s: %s',
                news.external_id,
                exc,
            )

    def _show_dry_run(self, feed):
        """Показать, что было бы сделано."""
        self.stdout.write('')
        self.stdout.write(
            self.style.WARNING('[DRY RUN] Запись в БД пропущена'),
        )
        self.stdout.write('')

        for i, post in enumerate(feed.posts[:10], 1):
            has_cover = '✓' if post.cover_url else '—'
            has_video = '🎥' if post.has_video else '—'
            self.stdout.write(
                f'  [{i}] {post.title[:60]:<60} '
                f'| {post.published_at:%d.%m.%Y} '
                f'| cover {has_cover} | video {has_video}',
            )

        if len(feed.posts) > 10:
            self.stdout.write(f'  ... и ещё {len(feed.posts) - 10}')
