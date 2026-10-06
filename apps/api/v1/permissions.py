"""Кастомные permissions для API."""

from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Разрешить редактирование только автору объекта или админу."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_staff or request.user.is_superuser:
            return True
        return obj.author == request.user
