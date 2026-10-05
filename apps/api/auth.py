"""JWT-эндпоинты для получения и обновления токенов."""

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


__all__ = ['TokenObtainPairView', 'TokenRefreshView']
