# coding=utf-8
import os

from rest_framework import serializers

from .models import Note


class NoteSerializer(serializers.ModelSerializer):
    """
    Details Description serializer with card id
    """

    class Meta:
        model = Note
        fields = ('id', 'card', 'text', 'image', 'audio', 'file')
        read_only_fields = ()


class NoteGenericSerializer(serializers.ModelSerializer):
    """
    Short Description serializer with file type
    """

    file_object = serializers.SerializerMethodField()
    created = serializers.DateTimeField(format='%a, %d %B %Y')
    time_created = serializers.DateTimeField(source='created', format='%H:%M')

    def get_file_object(self, note):
        if note.image:
            return {
                'type': note.FILE_TYPES.IMAGE,
                'url': note.image.url,
                'thumb_url': '%s_thumbnail%s' % os.path.splitext(note.image.url),
                'name': os.path.basename(note.image.url),
                'duration': 0
            }
        elif note.audio:
            return {
                'type': note.FILE_TYPES.AUDIO,
                'url': note.audio.url,
                'thumb_url': '',
                'name': os.path.basename(note.audio.url),
                'duration': note.audio_duration
            }
        elif note.file:
            return {
                'type': note.FILE_TYPES.OTHER,
                'url': note.file.url,
                'thumb_url': '',
                'name': os.path.basename(note.file.name),
                'duration': 0
            }
        else:
            return None

    class Meta(object):
        model = Note
        fields = ('id', 'card', 'text', 'file_object', 'created', 'time_created')


class NoteByDateSerializer(serializers.Serializer):
    date = serializers.DateTimeField(format='%a, %d %B %Y')
    iso_date = serializers.DateTimeField(format='%d.%m.%Y')
    items = NoteGenericSerializer(many=True)

    class Meta:
        fields = ("date", "iso_date", "items")
