"""Контекстные процессоры — данные, доступные во всех шаблонах."""

from django.conf import settings


def site_meta(request):
    """Информация о сайте — имя, описание, ключевые слова."""
    return {
        'site_name': settings.SITE_NAME,
        'site_description': settings.SITE_DESCRIPTION,
        'site_keywords': settings.SITE_KEYWORDS,
        'site_url': settings.SITE_URL,
    }
