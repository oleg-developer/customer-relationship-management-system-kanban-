from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import mixins, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from nc_auth.serializers.user import UserShortSerializer, UserDetailSerializer
from . import PERMISSION_CLASSES
from ...models import Column, Board


class UserColumnRelationView(APIView):
    """
    API Добавления участника на этап
    """
    serializer_class = UserShortSerializer
    permission_classes = PERMISSION_CLASSES

    def get_users_queryset(self):
        return get_user_model().objects.filter(company_id=self.request.user.company_id, is_active=True)

    def get_columns_queryset(self):
        return Column.objects.filter(board__company_id=self.request.user.company_id)

    def post(self, request):
        """
        API Добавления участника на этап
        ```
        {
            "accountId": int,
            "columnId": int
        }
        ```
        """
        try:
            user = self.get_users_queryset().get(id=request.data["accountId"])
            column = self.get_columns_queryset().get(id=request.data["columnId"])
        except (settings.AUTH_USER_MODEL.DoesNotExist, Column.DoesNotExist) as e:
            return Response(str(e), status=status.HTTP_403_FORBIDDEN)
        column.users.add(user)
        return Response(self.serializer_class(user).data, status=status.HTTP_201_CREATED)

    def delete(self, request):
        """
        API Удаления участника с этапа
        ```
        {
            "accountId": int,
            "columnId": int
        }
        ```
        """
        try:
            user = self.get_users_queryset().get(id=request.data["accountId"])
            column = self.get_columns_queryset().get(id=request.data["columnId"])
        except (settings.AUTH_USER_MODEL.DoesNotExist, Column.DoesNotExist) as e:
            return Response("Column or User does not exists or isn't accessible", status=status.HTTP_404_NOT_FOUND)
        column.user.remove(user)

        return Response(status=status.HTTP_204_NO_CONTENT)


class BoardUsersViewSet(mixins.ListModelMixin, GenericViewSet):
    """
    API Получение списка всех аккаунтов на доске
    """

    serializer_class = UserDetailSerializer
    permission_classes = PERMISSION_CLASSES

    def check_permissions(self, request):
        super(BoardUsersViewSet, self).check_permissions(request)
        if self.lookup_field in self.kwargs and not Board.objects.filter(
                company_id=self.request.user.company_id,
                id=self.kwargs[self.lookup_field]
        ).exists():
            self.permission_denied(
                request, message="Board does not exists or isn't accessible"
            )

    def get_queryset(self):
        return get_user_model().objects.filter(column__board_id=self.kwargs[self.lookup_field]).distinct() \
            .select_related("user")
