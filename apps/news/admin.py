from django.contrib import admin

from .models import Comment, NewsPost


class CommentInline(admin.TabularInline):
    """Инлайн комментариев в новости."""

    model = Comment
    extra = 0
    fields = ('author', 'text', 'is_published', 'created_at')
    readonly_fields = ('created_at',)
    show_change_link = True


@admin.register(NewsPost)
class NewsPostAdmin(admin.ModelAdmin):
    """Новости команды — свои и из ВК."""

    list_display = (
        'title',
        'source',
        'external_id',
        'has_video',
        'author',
        'is_published',
        'published_at',
    )
    list_filter = (
        'source',
        'is_published',
        'has_video',
        'published_at',
    )
    search_fields = (
        'title',
        'content',
        'external_id',
    )
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'
    inlines = [CommentInline]

    readonly_fields = (
        'external_id',
        'external_url',
    )

    fieldsets = (
        (
            'Основное',
            {
                'fields': (
                    'title',
                    'slug',
                    'excerpt',
                    'content',
                    'cover',
                    'author',
                    'is_published',
                ),
            },
        ),
        (
            'Источник',
            {
                'fields': (
                    'source',
                    'external_id',
                    'external_url',
                    'has_video',
                ),
                'classes': ('collapse',),
            },
        ),
        (
            'Даты',
            {
                'fields': (
                    'published_at',
                    'updated_at',
                ),
            },
        ),
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'post',
        'short_text',
        'is_published',
        'created_at',
    )
    list_filter = ('is_published', 'created_at')
    search_fields = ('text', 'author__username')
    raw_id_fields = ('author', 'post')
    actions = ['publish_comments', 'unpublish_comments']

    @admin.display(description='Текст')
    def short_text(self, obj):
        """Обрезанный текст для списка."""
        return obj.text[:50]

    @admin.action(description='Опубликовать выбранные')
    def publish_comments(self, request, queryset):
        queryset.update(is_published=True)

    @admin.action(description='Скрыть выбранные')
    def unpublish_comments(self, request, queryset):
        queryset.update(is_published=False)
