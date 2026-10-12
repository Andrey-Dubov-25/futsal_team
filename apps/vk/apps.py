from django.apps import AppConfig
from django.contrib import admin
from django.urls import path

from apps.vk import admin as vk_admin


class VkConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.vk'
    verbose_name = 'ВКонтакте'

    def ready(self):
        """Регистрируем кастомный URL в admin site."""

        # Добавляем URL в admin
        original_get_urls = admin.site.get_urls

        def get_urls():
            urls = original_get_urls()
            custom_urls = [
                path(
                    'vk/sync/',
                    admin.site.admin_view(vk_admin.sync_vk_view),
                    name='vk-sync',
                ),
            ]
            return custom_urls + urls

        admin.site.get_urls = get_urls
