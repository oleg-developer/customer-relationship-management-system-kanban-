# coding=utf-8
import os
from collections import defaultdict

from django.http import HttpResponse, HttpResponseNotFound
from rest_framework import mixins
from rest_framework.decorators import detail_route
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from nc_auth.permissions import IsAuthenticated
from .models import Note
from .serializers import NoteSerializer, NoteByDateSerializer


class NotesOfCardView(GenericViewSet):
    """
    List of descriptions
    """
    renderer_classes = (BrowsableAPIRenderer, JSONRenderer)
    queryset = Note.objects.all().order_by('id')
    permission_classes = (IsAuthenticated,)  # TODO
    serializer_class = NoteByDateSerializer

    def get_queryset(self):
        return self.queryset.filter(card__id=self.kwargs.get('card_id', None))

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        notes_by_date = defaultdict(list)
        for note in queryset:
            notes_by_date[note.created.date()].append(note)
        notes_by_date = [{
            "date": date,
            "iso_date": date,
            "items": notes
        } for date, notes in notes_by_date.items()]

        serializer = self.get_serializer(notes_by_date, many=True)
        return Response(serializer.data)


class NotesViewSet(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   GenericViewSet):
    queryset = Note.objects.all()
    permission_classes = (IsAuthenticated,)  # TODO

    def get_serializer_class(self):
        return {
            "create": NoteSerializer,
            "retrieve": NoteSerializer,
            "update": NoteSerializer,
            "partial_update": NoteSerializer
        }.get(self.action, NoteSerializer)

    @detail_route(methods=["get"])
    def download(self, request, *args, **kwargs):
        note = self.get_object()
        if not note:
            return HttpResponseNotFound()
        # TODO: Audio & image?
        response = HttpResponse(note.file.open("r").read(), content_type='application/x-download')
        response['Content-Disposition'] = 'attachment;filename="%s"' % os.path.basename(note.file.name).encode('utf8')
        return response

    @detail_route(methods=['get'])
    def pdf_viewer(self, request, *args, **kwargs):
        response = self.download(request, *args, **kwargs)
        response['Content-Type'] = 'application/pdf'
        return response
