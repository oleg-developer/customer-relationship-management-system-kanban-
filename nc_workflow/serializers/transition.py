from rest_framework import serializers

from nc_workflow.models import Column, Transition


class TransitionSerializer(serializers.ModelSerializer):
    _from = serializers.PrimaryKeyRelatedField(queryset=Column.objects.all(), source='from_column', required=True)
    to = serializers.PrimaryKeyRelatedField(queryset=Column.objects.all(), source='to_column', required=True)

    class Meta:
        model = Transition
        fields = ('id', 'active', 'from', 'to')
        read_only_fields = ('active',)

    def to_representation(self, instance: Transition):
        return {
            "id": instance.id,
            "active": instance.active,
            "is_end_workflow": instance.from_column.is_end_workflow,
            "is_start_workflow": instance.from_column.is_start_workflow,
            "from_column": instance.from_column_id,
            "to_column": instance.to_column_id,
            "title": instance.from_column.title
        }


# This hack is required to create field `from`
TransitionSerializer._declared_fields["from"] = TransitionSerializer._declared_fields["_from"]
del TransitionSerializer._declared_fields["_from"]
