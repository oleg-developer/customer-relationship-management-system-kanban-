from django.shortcuts import get_object_or_404
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from nc_workflow.models import Column
from . import PERMISSION_CLASSES
from ...models import Board
from ...serializers.board import BoardBaseSerializer
from ...serializers.column import ColumnSerializer


class BoardAdminViewSet(ModelViewSet):
    serializer_class = BoardBaseSerializer
    permission_classes = PERMISSION_CLASSES

    def get_queryset(self):
        return Board.objects.filter(company_id=self.request.user.company_id)

    def perform_create(self, serializer):
        serializer.save(company_id=self.request.user.company_id)

    @detail_route(methods=['get', 'put'])
    def stages(self, request, *args, **kwargs):
        """
        - GET: Получение списка колонок по доске
        - PUT: Перетаскивание колонки на другую позицию (Сохранение позиции этапа)

        В ответе все колонки относительно текущей доски с уже измененными position,
        """
        qs = Column.objects.filter(board_id=self.kwargs[self.lookup_field],
                                   board__company_id=self.request.user.company_id)
        if request.method == "PUT":
            column = get_object_or_404(qs, id=kwargs['pk'])
            serializer = ColumnSerializer(instance=column, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        response = ColumnSerializer(instance=qs, many=True)
        return Response(response.data)
