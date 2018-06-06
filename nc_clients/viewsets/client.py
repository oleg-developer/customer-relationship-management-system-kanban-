from django.http import HttpResponseBadRequest
from django.utils.text import slugify
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from unidecode import unidecode

from ..models import Client, ClientExtraTypeFace
from ..serializers import ClientSerializer, ClientDetailedSerializer


class ClientViewSet(ModelViewSet):
    model = Client
    permission_classes = (IsAuthenticated,)
    queryset = Client.objects.all()

    def perform_create(self, serializer):
        serializer.save(user_created=self.request.user, user_modified=self.request.user, owner=self.request.user)

    def get_serializer_class(self):
        return (ClientDetailedSerializer
                if self.action in {"create", "retrieve", "update", "partial_update"}
                else ClientSerializer)


@api_view(["POST", "DELETE"])
@permission_classes((IsAuthenticated,))
def client_relations(request, pk, other_pk):
    """
    Create or delete relation between two clients
    """
    client = get_object_or_404(Client, id=pk)
    other_client = get_object_or_404(Client, id=other_pk)
    if client == other_client:
        return HttpResponseBadRequest("Client == OtherClient")
    if request.method.upper() == "POST":
        client.relations.add(other_client)
    elif request.method.upper() == "DELETE":
        client.relations.remove(other_client)
    return Response(ClientSerializer(client.relations, many=True).data)


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def get_type_faces(request):
    """
    Return list of face types
    """
    user = request.user
    return Response(
        [{"label": verbose, "name": value}
         for value, verbose in Client.FACE_CHOICES if value != "other"]
        +
        [{"label": t.value, "name": slugify(unidecode(t.value)) + "_"}
         for t in ClientExtraTypeFace.objects.filter(user=user)]
    )
