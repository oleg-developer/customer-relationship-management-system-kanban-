from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.views import APIView

from nc_auth.permissions import IsAuthenticated, HasCompanyRelation
from nc_clients.models import Client
from nc_clients.serializers import ClientSerializer
from ..models import Card
from ..serializers.card import CardDetailSerializer


class CardViewSet(viewsets.ModelViewSet):
    lookup_value_regex = r"[0-9]+"
    permission_classes = (IsAuthenticated, HasCompanyRelation)
    serializer_class = CardDetailSerializer

    def get_queryset(self):
        return Card.objects.select_related("client", "column__board").all()

    def filter_queryset(self, queryset):
        queryset = queryset.filter(status=Card.STATUS_CHOICES.ACTIVE, company_id=self.request.user.company_id)
        return super(CardViewSet, self).filter_queryset(queryset)

    def perform_create(self, serializer):
        serializer.save(user_created=self.request.user, user_modified=self.request.user,
                        owner=self.request.user, company_id=self.request.user.company_id)

    def perform_update(self, serializer):
        serializer.save(user_modified=self.request.user)

    def destroy(self, request, *args, **kwargs):
        card = self.get_object()
        card.status = Card.STATUS_CHOICES.BASKET
        card.column = None
        card.save()
        return Response(self.serializer_class(card).data, status=status.HTTP_200_OK)


class CardClientAPIView(APIView):
    permission_classes = (IsAuthenticated, HasCompanyRelation)

    def get_querysets(self):
        cards = Card.objects.select_related("client").filter(company_id=self.request.user.company_id)
        clients = Client.objects.all()  # TODO: Filter by company
        return cards, clients

    def get_objects(self):
        cards, clients = self.get_querysets()
        client_pk = self.kwargs["client_pk"]
        return (
            get_object_or_404(cards, id=self.kwargs["card_pk"]),
            get_object_or_404(clients, id=client_pk) if client_pk else None
        )

    def get(self, request, *args, **kwargs):
        card, _ = self.get_objects()
        client = card.client
        return Response(ClientSerializer(client).data if client else {}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        card, client = self.get_objects()
        if client is None:
            raise Http404("`client_pk` is required for method POST")
        card.client = client
        card.save()
        return Response(ClientSerializer(client).data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        card, client = self.get_objects()
        card.client = None
        card.save()
        return Response({}, status=status.HTTP_204_NO_CONTENT)


class CardRestoreMixin(object):
    """
    Восстановление карточку на указанную колонку
    """

    def update(self, request, *args, **kwargs):
        if "column" not in request.data:
            return Response({"detail": "column is required"}, status=status.HTTP_400_BAD_REQUEST)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data={
                "column": request.data["column"],
                "position": instance.position
            },
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class CardArchiveViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, CardRestoreMixin, viewsets.GenericViewSet):
    lookup_value_regex = r"[0-9]+"
    # TODO: Archive permissions
    permission_classes = (IsAuthenticated, HasCompanyRelation)
    serializer_class = CardDetailSerializer

    def get_queryset(self):
        return Card.objects.select_related("client", "column__board").all()

    def filter_queryset(self, queryset):
        queryset = queryset.filter(status=Card.STATUS_CHOICES.ARCHIVE, company_id=self.request.user.company_id)
        return super(CardArchiveViewSet, self).filter_queryset(queryset)


class CardBasketViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        CardRestoreMixin,
                        mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    lookup_value_regex = r"[0-9]+"
    # TODO: Отдельные права
    permission_classes = (IsAuthenticated, HasCompanyRelation)
    serializer_class = CardDetailSerializer

    def get_queryset(self):
        return Card.objects.select_related("client", "column__board").all()

    def filter_queryset(self, queryset):
        queryset = queryset.filter(status=Card.STATUS_CHOICES.BASKET, company_id=self.request.user.company_id)
        return super(CardBasketViewSet, self).filter_queryset(queryset)

    def destroy_all(self, request, *args, **kwargs):
        cards = self.get_queryset()
        cards.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
