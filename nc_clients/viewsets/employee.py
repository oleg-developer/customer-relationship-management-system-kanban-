from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from ..models import Employee
from ..serializers import EmployeeSerializer


class EmployeeViewSet(mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      GenericViewSet):
    """Haven't List action"""
    model = Employee
    permission_classes = (IsAuthenticated,)
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    def perform_create(self, serializer):
        serializer.save(user_created=self.request.user, user_modified=self.request.user,
                        owner=self.request.user.account)

    def perform_update(self, serializer):
        serializer.save(user_modified=self.request.user)
