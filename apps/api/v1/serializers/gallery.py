"""Сериализаторы фотогалереи."""

from rest_framework import serializers

from apps.gallery.models import Album, Photo


class PhotoSerializer(serializers.ModelSerializer):
    """Сериализатор фотографии."""

    class Meta:
        model = Photo
        fields = ['id', 'image', 'caption', 'order', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']


class AlbumListSerializer(serializers.ModelSerializer):
    """Краткая информация об альбоме (для списка)."""

    photos_count = serializers.IntegerField(read_only=True)
    match_opponent = serializers.CharField(
        source='match.opponent',
        read_only=True,
    )

    class Meta:
        model = Album
        fields = [
            'id',
            'title',
            'slug',
            'description',
            'cover',
            'date',
            'match',
            'match_opponent',
            'photos_count',
            'is_published',
            'order',
        ]
        read_only_fields = ['id', 'slug']


class AlbumDetailSerializer(serializers.ModelSerializer):
    """Детальная информация об альбоме — с фотографиями."""

    photos = PhotoSerializer(many=True, read_only=True)
    match_opponent = serializers.CharField(
        source='match.opponent',
        read_only=True,
    )

    class Meta:
        model = Album
        fields = [
            'id',
            'title',
            'slug',
            'description',
            'cover',
            'date',
            'match',
            'match_opponent',
            'is_published',
            'order',
            'photos',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']
