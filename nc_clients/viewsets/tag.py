from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework.decorators import detail_route, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from ..models import Tag, Client
from ..serializers import TagSerializer, ClientSerializer


class TagViewSet(ReadOnlyModelViewSet):
    model = Tag
    permission_classes = (IsAuthenticated,)
    queryset = Tag.objects.annotate(counter=Count("client"))
    serializer_class = TagSerializer

    @detail_route(["GET"], permission_classes=(IsAuthenticated,))
    def clients(self, *args, **kwargs):
        tag = self.get_object()
        return Response(ClientSerializer(tag.client_set.all(), many=True).data)


@api_view(["POST", "DELETE"])
@permission_classes((IsAuthenticated,))
def client_tag(request, client_pk, tag_pk=None):
    """Add/remove client's tag"""
    client = get_object_or_404(Client, id=client_pk)
    if request.method.upper() == "POST":
        client.tag = get_object_or_404(Tag, id=tag_pk)
        client.save()
    elif request.method.upper() == "DELETE":
        client.tag = None
        client.save()
    return Response(ClientSerializer(client).data)
