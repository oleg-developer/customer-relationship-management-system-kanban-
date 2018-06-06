from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from .column import ColumnWorkflowSerializer
from ..models import Column, Subprocess


class SubprocessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subprocess
        fields = ('column_to', 'column_from')

    def validate(self, data):
        if data['column_from'].board_id == data['column_to'].board_id:
            raise serializers.ValidationError(_("The selected source board is equal destination board"))
        return data

    def save(self, **kwargs):
        super(SubprocessSerializer, self).save(**kwargs)
        Column.is_subprocess.fget.clear_cache(self.instance.column_to)
        return self.instance

    def to_representation(self, subprocess: Subprocess):
        board_to_columns = ColumnWorkflowSerializer(instance=subprocess.column_to.board.columns.all(), many=True)
        return {
            "columns": board_to_columns.data,
            "target_column": subprocess.column_to_id,
            "title": subprocess.column_to.board.title,
            "id": subprocess.column_to.board_id
        }
