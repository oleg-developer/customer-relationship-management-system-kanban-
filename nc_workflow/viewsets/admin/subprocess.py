from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from rest_framework import mixins, status
from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from nc_workflow.models import Column
from . import PERMISSION_CLASSES
from ...models import Subprocess
from ...serializers.subprocess import SubprocessSerializer


class SubprocessViewSet(mixins.CreateModelMixin,
                        mixins.ListModelMixin,
                        GenericViewSet):
    """
    API Создание перехода на доску
    Создает модель прехода Subprocess и возвращает колонку куда был переход и все колонки вместе с ней
    """
    queryset = Subprocess.objects.select_related("column_from__board").select_related("column_to__board").all()
    permission_classes = PERMISSION_CLASSES
    serializer_class = SubprocessSerializer

    def filter_queryset(self, queryset):
        return queryset.filter(Q(column_from__board__company_id=self.request.user.company_id)
                               | Q(column_to__board__company_id=self.request.user.company_id))

    @list_route(methods=['delete'])
    def custom_destroy(self, request, *args, **kwargs):
        subprocess = get_object_or_404(
            self.get_queryset(),
            column_from_id=request.data.get("column_from", None),
            column_to_id=request.data.get("column_to", None)
        )
        Column.is_subprocess.fget.clear_cache(subprocess.column_to)
        subprocess.delete()
        return Response({'detail': _("successful delete")}, status=status.HTTP_204_NO_CONTENT)
