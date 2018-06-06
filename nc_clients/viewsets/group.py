from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework.decorators import detail_route, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from ..models import Group, Client
from ..serializers import GroupSerializer, GroupDetailedSerializer, ClientSerializer


class GroupViewSet(ModelViewSet):
    model = Group
    permission_classes = (IsAuthenticated,)
    queryset = Group.objects.annotate(counter=Count("client"))
    serializer_class = GroupSerializer

    @detail_route(["GET"], permission_classes=(IsAuthenticated,))
    def clients(self, *args, **kwargs):
        """
        Clients list of given group
        """
        group = self.get_object()
        return Response(ClientSerializer(group.client_set.all(), many=True).data)

    def get_serializer_class(self):
        return (GroupDetailedSerializer
                if self.action in {"retrieve", "update", "partial_update"}
                else GroupSerializer)


@api_view(["POST", "DELETE"])
@permission_classes((IsAuthenticated,))
def client_group(request, client_pk, group_pk=None):
    """Add or remove client to/from group"""
    client = get_object_or_404(Client, id=client_pk)
    if request.method.upper() == "POST":
        client.group = get_object_or_404(Group, id=group_pk)
        client.save()
    elif request.method.upper() == "DELETE":
        client.group = None
        client.save()
    return Response(ClientSerializer(client).data)
