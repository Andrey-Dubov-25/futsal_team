"""Админка ВКонтакте.

Приложение не имеет моделей — только management-команда sync_vk.
Здесь добавляем кнопку синхронизации в главное меню админки.
"""

from io import StringIO

from django.contrib import admin, messages
from django.core.management import call_command
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse


class VkSyncAdminSite(admin.AdminSite):
    """Расширение админки — добавляем страницу синхронизации ВК."""

    pass  # используем стандартный admin site


def sync_vk_view(request):
    """View для запуска sync_vk из админки."""

    if request.method == 'POST':
        output = StringIO()
        try:
            call_command('sync_vk', stdout=output)
            result = output.getvalue()

            # Показываем сообщение и результат
            messages.success(
                request,
                'Синхронизация ВК завершена',
            )
            return TemplateResponse(
                request,
                'admin/vk/sync_result.html',
                {
                    'title': 'Синхронизация ВК',
                    'result': result,
                },
            )
        except Exception as exc:
            messages.error(request, f'Ошибка: {exc}')
            return HttpResponseRedirect(
                reverse('admin:index'),
            )

    # GET — показываем страницу с кнопкой
    return TemplateResponse(
        request,
        'admin/vk/sync_form.html',
        {
            'title': 'Синхронизация ВКонтакте',
        },
    )
