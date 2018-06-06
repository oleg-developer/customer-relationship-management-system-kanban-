from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from . import PERMISSION_CLASSES
from ...models import Column
from ...serializers.column import ColumnStagesSerializer, ColumnWithAccountsSerializer, ColumnTransitionSerializer, \
    ColumnSubprocessSerializer


def filter_columns(qs, request):
    return qs.filter(board__company_id=request.user.company_id)


class StagesViewSet(mixins.CreateModelMixin,
                    mixins.DestroyModelMixin,
                    mixins.UpdateModelMixin,
                    GenericViewSet):
    """
    API Создание колонок на позиции/перетаскивание и тд
    """
    queryset = Column.objects.all()
    permission_classes = PERMISSION_CLASSES
    serializer_class = ColumnStagesSerializer

    def filter_queryset(self, queryset):
        return filter_columns(queryset, self.request)


class ColumnsWithAccountsViewSet(mixins.ListModelMixin, GenericViewSet):
    """
    API Получения колонок доски с аккаунтами
    """
    serializer_class = ColumnWithAccountsSerializer
    permission_classes = PERMISSION_CLASSES

    def get_queryset(self):
        board_pk = self.kwargs['pk']
        return Column.objects.filter(board_id=board_pk).prefetch_related("users")

    def filter_queryset(self, queryset):
        return filter_columns(queryset, self.request)


class BoardGetTransitionsViewSet(mixins.ListModelMixin, GenericViewSet):
    """
    API Получение доски - переход карточки
    В колонке нет параметра active, поэтому соотвественно он не отдается
    Возвращает все указанные параметры кроме activ,т.к у колонки нет такого параметра.
    В данный момент на фронте он не нужен, но иметь ввиду что может понадобится.
    """
    serializer_class = ColumnTransitionSerializer
    permission_classes = PERMISSION_CLASSES

    def get_queryset(self):
        board_pk = self.kwargs['pk']
        return Column.objects.prefetch_related("subprocess_from__column_to__board__columns").filter(board_id=board_pk)

    def filter_queryset(self, queryset):
        return filter_columns(queryset, self.request)


class BoardGetSubprocessViewSet(mixins.ListModelMixin, GenericViewSet):
    """
    API Получение доски - переход на доску
    """
    serializer_class = ColumnSubprocessSerializer
    permission_classes = PERMISSION_CLASSES

    def get_queryset(self):
        board_pk = self.kwargs['pk']
        return Column.objects.filter(board_id=board_pk)

    def filter_queryset(self, queryset):
        return filter_columns(queryset, self.request)

    # def list(self, request, *args, **kwargs):
    #     resp = super(BoardGetSubprocessViewSet, self).list(request, *args, **kwargs)
    #     subprocess_boards = list(chain(*[col['subprocess'] for col in resp.data]))
    #     for col in resp.data:
    #         col['subprocess_boards'] = subprocess_boards
    #     return resp
