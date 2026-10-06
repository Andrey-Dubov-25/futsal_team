"""View для аутентификации и профиля пользователя."""

from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.api.v1.serializers import (
    RegisterSerializer,
    UpdateProfileSerializer,
    UserSerializer,
)


User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """Регистрация нового пользователя.

    Доступна анонимно. После успешной регистрации возвращает
    данные пользователя и пару JWT-токенов.
    """

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        user_data = UserSerializer(user).data

        return Response(
            {
                'user': user_data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            status=status.HTTP_201_CREATED,
        )


class MeView(generics.RetrieveUpdateAPIView):
    """Профиль текущего пользователя.

    GET — вернуть профиль.
    PATCH — обновить first_name, last_name, phone, avatar.
    """

    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return UpdateProfileSerializer
        return UserSerializer


class LogoutView(APIView):
    """Отозвать refresh-токен (logout)."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except KeyError:
            return Response(
                {'detail': 'Поле refresh обязательно.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception:
            return Response(
                {'detail': 'Невалидный токен.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
