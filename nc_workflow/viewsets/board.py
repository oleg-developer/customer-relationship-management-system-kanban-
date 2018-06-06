from django.db import transaction
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from rest_framework import status
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from nc_auth.permissions import IsAuthenticated, HasCompanyRelation
from ..models import Board, Card
from ..serializers.board import BoardSerializer, BoardDetailSerializer
from ..serializers.card import CardDetailSerializer


class BoardFilter(filters.FilterSet):
    exclude = filters.Filter(field_name="id", exclude=True, label="Exclude item by id")

    class Meta:
        model = Board
        fields = ['exclude']


class BoardViewSet(ReadOnlyModelViewSet):
    lookup_value_regex = r"[0-9]+"
    permission_classes = (IsAuthenticated, HasCompanyRelation)
    filter_class = BoardFilter

    def get_queryset(self):
        qs = Board.objects.all()
        if self.action in ("retrieve",):
            qs = qs.prefetch_related(
                "columns__cards",
                "columns__transitions_from",
                "columns__transitions_to",
                "columns__users",
                # "columns__subprocess_from",
                # "columns__subprocess_to"
            )
        else:
            return qs.prefetch_related("columns")
        return qs

    def filter_queryset(self, queryset):
        queryset = queryset.filter(company_id=self.request.user.company_id)
        return super(BoardViewSet, self).filter_queryset(queryset)

    def get_cards_queryset(self):
        return Card.objects.filter(company_id=self.request.user.company_id, status=Card.STATUS_CHOICES.ACTIVE)

    def get_serializer_class(self):
        return {
            "list": BoardSerializer,
            "card": CardDetailSerializer,
            "cards": CardDetailSerializer
        }.get(self.action, BoardDetailSerializer)

    @list_route(methods=['put'])
    def cards(self, request):
        "Обновление карточек списком"
        # TODO: Permissions?
        queryset = self.get_cards_queryset()
        serializers = []
        for card_data in request.data:
            card = get_object_or_404(queryset, id=card_data["id"])
            serializer = CardDetailSerializer(card, data=card_data)
            serializer.is_valid(raise_exception=True)
            serializers.append(serializer)

        with transaction.atomic():
            for serializer in serializers:
                serializer.save()

        return Response({"details": "successful update"}, status=status.HTTP_200_OK)

    @detail_route(methods=['post'])
    def card(self, request, *args, **kwargs):
        """
        Создание карточки на первой колонке указанной доски
        """
        # TODO: Permissions?
        board = self.get_object()
        serializer_card = CardDetailSerializer(
            data={
                'column': board.column_workflow_start.id,
                'company': request.user.company_id,
                'title': request.data.get('title', '')
            }
        )
        serializer_card.is_valid(raise_exception=True)
        serializer_card.save(user_created=self.request.user, user_modified=self.request.user,
                             owner=self.request.user, company_id=self.request.user.company_id)
        return Response(serializer_card.data)
