from rest_framework import serializers

from ..models import Board
from ..serializers.column import ColumnWorkflowSerializer, ColumnNestedSerializer


class BoardBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = (
            'id',
            'title',
            'position',
        )


class BoardSerializer(serializers.ModelSerializer):
    columns = ColumnWorkflowSerializer(many=True, read_only=True)
    column_workflow_start = ColumnWorkflowSerializer(read_only=True)

    class Meta:
        model = Board
        fields = (
            'id',
            'title',
            'position',
            'column_workflow_start',
            'columns',
        )


class BoardDetailSerializer(BoardSerializer):
    columns = ColumnNestedSerializer(many=True, read_only=True)


# TODO: Refactor
class BoardChangePermissionsSerializer(serializers.Serializer):
    class ResponsibleSerializer(serializers.ModelSerializer):
        class Meta:
            # model = Responsible
            fields = (
                'account',
            )

    class PermissionsBoardAccountSerializer(serializers.ModelSerializer):
        class Meta:
            model = None
            fields = (
                'board',
            )

    def validate(self, attrs):
        def subvalidate(item):
            account = self.ResponsibleSerializer(data={'account': item['user_id']})
            account.is_valid(raise_exception=True)
            # Проверка storage_rights по полям
            # storage = PermissionsAccountSerializer(data=item['storage_rights'])
            # storage.is_valid(raise_exception=True)
            # TODO: !!! Проверка modules, когда они будут дописаны !!!
            return True

        board = self.PermissionsBoardAccountSerializer(data={'board': self.context['board_id']})
        board.is_valid(raise_exception=True)
        return [{
            'account': Account.objects.get(id=item['user_id']),
            'board': Board.objects.get(id=board.data['board']),
            'storage': item['storage_rights']
        } for item in self.context['data'] if subvalidate(item)]
