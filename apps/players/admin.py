from django.contrib import admin

from .models import Player


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = (
        'number',
        'last_name',
        'first_name',
        'position',
        'is_active',
    )
    list_filter = ('position', 'is_active')
    search_fields = ('first_name', 'last_name', 'nickname')
    ordering = ('number',)
