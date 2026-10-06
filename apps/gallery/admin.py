from django.contrib import admin

from .models import Album, Photo


class PhotoInline(admin.TabularInline):
    """Инлайн фотографий в альбоме."""

    model = Photo
    extra = 1
    fields = ('image', 'caption', 'order')
    ordering = ('order',)


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'is_published', 'order')
    list_filter = ('is_published', 'date')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'date'
    raw_id_fields = ('match',)
    list_editable = ('is_published', 'order')
    inlines = [PhotoInline]


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'album', 'order', 'uploaded_at')
    list_filter = ('album',)
    search_fields = ('caption',)
    raw_id_fields = ('album',)
    list_editable = ('order',)
