from django.contrib import admin

from .models import Training


@admin.register(Training)
class TrainingAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'location', 'coach', 'is_cancelled')
    list_filter = ('is_cancelled', 'date')
    search_fields = ('title', 'location')
    date_hierarchy = 'date'
    raw_id_fields = ('coach',)
    list_editable = ('is_cancelled',)
