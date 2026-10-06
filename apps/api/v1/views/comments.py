"""ViewSet комментариев."""

from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.api.v1.permissions import IsAuthorOrReadOnly
from apps.api.v1.serializers import (
    CommentCreateSerializer,
    CommentSerializer,
)
from apps.news.models import Comment, NewsPost


class CommentViewSet(viewsets.ModelViewSet):
    """CRUD-эндпоинт комментариев.

    - GET /api/v1/comments/?post=<slug> — список комментариев к новости.
    - POST /api/v1/comments/ — создать (только авторизованные).
    - DELETE /api/v1/comments/{id}/ — удалить (автор или админ).
    """

    permission_classes = [IsAuthorOrReadOnly]
    serializer_class = CommentSerializer

    def get_queryset(self):
        qs = Comment.objects.select_related(
            'author',
            'post',
        ).filter(is_published=True)

        post_slug = self.request.query_params.get('post')
        if post_slug:
            qs = qs.filter(post__slug=post_slug)

        return qs

    def get_serializer_class(self):
        if self.action == 'create':
            return CommentCreateSerializer
        return CommentSerializer

    def get_permissions(self):
        if self.action in ('create',):
            return [IsAuthenticated()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        """Создать комментарий и вернуть его в формате для чтения."""
        write_serializer = self.get_serializer(data=request.data)
        write_serializer.is_valid(raise_exception=True)
        comment = self.perform_create(write_serializer)

        read_serializer = CommentSerializer(
            comment,
            context=self.get_serializer_context(),
        )
        headers = self.get_success_headers(read_serializer.data)
        return Response(
            read_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def perform_create(self, serializer):
        """Привязать комментарий к новости и автору."""
        post_slug = self.request.data.get('post')
        post = NewsPost.objects.get(slug=post_slug)
        return serializer.save(author=self.request.user, post=post)
