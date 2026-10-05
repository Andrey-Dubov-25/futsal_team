"""Сериализаторы новостей."""

from rest_framework import serializers

from apps.news.models import NewsPost


class NewsPostSerializer(serializers.ModelSerializer):
    """Сериализатор новости."""

    author_username = serializers.CharField(
        source='author.username', read_only=True
    )

    class Meta:
        model = NewsPost
        fields = [
            'id',
            'title',
            'slug',
            'cover',
            'excerpt',
            'content',
            'author',
            'author_username',
            'is_published',
            'published_at',
        ]
        read_only_fields = ['slug', 'published_at']
