from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from rest_framework import mixins, status
from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from . import PERMISSION_CLASSES
from ...models import Transition
from ...serializers.transition import TransitionSerializer


class TransitionsViewSet(mixins.CreateModelMixin,
                         mixins.DestroyModelMixin,
                         # mixins.ListModelMixin,
                         GenericViewSet):
    """
    API Добавление перехода карточки
    Создает модель прехода Transition
    """

    queryset = Transition.objects.all()
    permission_classes = PERMISSION_CLASSES
    serializer_class = TransitionSerializer

    def filter_queryset(self, queryset):
        return queryset.filter(from_column__board__company_id=self.request.user.company_id)

    @list_route(methods=['delete'])
    def destroy_transitions(self, request, *args, **kwargs):
        transition = get_object_or_404(self.get_queryset(),
                                       from_column_id=request.data.get("from", None),
                                       to_column_id=request.data.get("to", None))
        transition.delete()
        return Response({'detail': _("successful delete")}, status=status.HTTP_204_NO_CONTENT)
