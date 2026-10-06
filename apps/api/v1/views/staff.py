"""ViewSet тренерского состава."""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from apps.api.v1.serializers import StaffSerializer
from apps.staff.models import Staff


class StaffViewSet(viewsets.ModelViewSet):
    """CRUD-эндпоинт сотрудников.

    Фильтры:
    - `?role=HEAD_COACH`
    - `?is_active=true`
    """

    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_fields = ['role', 'is_active']
    search_fields = ['first_name', 'last_name']
    ordering_fields = ['order', 'last_name']
    ordering = ['order', 'last_name']
