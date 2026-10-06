"""Сериализаторы комментариев."""

from rest_framework import serializers

from apps.news.models import Comment
from config import constants as c

from .auth import UserSerializer


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор комментария."""

    author = UserSerializer(read_only=True)
    post_slug = serializers.CharField(
        source='post.slug',
        read_only=True,
    )

    class Meta:
        model = Comment
        fields = [
            'id',
            'post',
            'post_slug',
            'author',
            'text',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'post', 'author', 'created_at', 'updated_at']

    def validate_text(self, value):
        """Проверить, что текст не пустой и не слишком длинный."""
        value = value.strip()
        if not value:
            raise serializers.ValidationError(
                'Текст комментария не может быть пустым.',
            )
        if len(value) > c.COMMENT_TEXT_MAX_LENGTH:
            raise serializers.ValidationError(
                f'Максимум {c.COMMENT_TEXT_MAX_LENGTH} символов.',
            )
        return value


class CommentCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания комментария (без вложенного author)."""

    class Meta:
        model = Comment
        fields = ['text']

    def validate_text(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError(
                'Текст комментария не может быть пустым.',
            )
        if len(value) > c.COMMENT_TEXT_MAX_LENGTH:
            raise serializers.ValidationError(
                f'Максимум {c.COMMENT_TEXT_MAX_LENGTH} символов.',
            )
        return value
