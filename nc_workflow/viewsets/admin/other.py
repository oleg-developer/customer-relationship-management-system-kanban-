from rest_framework import mixins, status
from rest_framework.response import Response
from rest_framework.views import APIView

from . import PERMISSION_CLASSES
from ...serializers.board import BoardChangePermissionsSerializer


class BoardChangePermissionsView(APIView, mixins.UpdateModelMixin):
    """
    API Изменения доступных для пользователя модулей
    Пока нет рабочего modules, в запрос передается только user_id, storage_rights
    TODO: DOPILIT!!!!!!
    """

    permission_classes = PERMISSION_CLASSES

    def post(self, request, *args, **kwargs):
        serializer = BoardChangePermissionsSerializer(data={'data': request.data},
                                                      context={'data': request.data, 'board_id': kwargs['pk']})
        serializer.is_valid(raise_exception=True)
        # Обновление данных доступа StorageRights
        response = []
        for item in serializer.validated_data:
            instance = item['account'].permission_account  # type: PermissionsAccount
            # update_serializer = PermissionsAccountSerializer(instance, data=item['storage'])
            # update_serializer.is_valid(raise_exception=True)
            # update_serializer.save()
            # TODO: !!! Обновление данных для модуля. Дописать когда будет готов модуль. !!!
            PermissionsBoardAccount.objects.get_or_create(board=item['board'], account=item['account'])
            response.append({
                "user_id": item['account'].id,
                "storage_rights": update_serializer.validated_data,
                "modules": "need develop"
            })
        return Response(response, status=status.HTTP_200_OK)
