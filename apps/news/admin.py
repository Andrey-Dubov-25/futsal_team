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
    list_display = ('title', 'author', 'is_published', 'published_at')
    list_filter = ('is_published', 'published_at')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [CommentInline]


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
