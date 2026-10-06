"""Сериализаторы аутентификации и профиля пользователя."""

from django.contrib.auth import get_user_model
from rest_framework import serializers

from config import constants as c


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Публичный профиль пользователя."""

    role_display = serializers.CharField(
        source='get_role_display',
        read_only=True,
    )

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'role',
            'role_display',
            'phone',
            'avatar',
        ]
        read_only_fields = ['id', 'username', 'role']


class RegisterSerializer(serializers.ModelSerializer):
    """Сериализатор регистрации нового пользователя."""

    password = serializers.CharField(
        write_only=True,
        min_length=c.USER_PASSWORD_MIN_LENGTH,
        style={'input_type': 'password'},
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
    )

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'password',
            'password_confirm',
        ]

    def validate_username(self, value):
        """Проверить, что username свободен."""
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError(
                'Пользователь с таким именем уже существует.',
            )
        return value

    def validate_email(self, value):
        """Проверить, что email свободен."""
        if value and User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                'Пользователь с таким email уже зарегистрирован.',
            )
        return value

    def validate(self, attrs):
        """Проверить, что пароли совпадают."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError(
                {'password_confirm': 'Пароли не совпадают.'},
            )
        return attrs

    def create(self, validated_data):
        """Создать пользователя с ролью болельщик по умолчанию."""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.role = User.Role.FAN
        user.save()
        return user


class UpdateProfileSerializer(serializers.ModelSerializer):
    """Сериализатор обновления профиля."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'avatar']
