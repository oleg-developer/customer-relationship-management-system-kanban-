from rest_framework import serializers

from nc_auth.serializers.user import UserShortSerializer
from .card import CardDetailSerializer
from ..models import Column, Subprocess


class ColumnNestedSerializer(serializers.ModelSerializer):
    class SubprocessDisplaySerializer(serializers.ModelSerializer):
        id = serializers.PrimaryKeyRelatedField(read_only=True, source='column_to')
        column_title = serializers.CharField(read_only=True, source='column_to.title')
        board_title = serializers.CharField(read_only=True, source='column_to.board.title')

        class Meta:
            model = Subprocess
            fields = ('id', 'column_title', 'board_title')

    cards = CardDetailSerializer(many=True, read_only=True)
    accounts = UserShortSerializer(many=True, read_only=True, source='users')
    transitions = serializers.SerializerMethodField()
    new_cards = serializers.SerializerMethodField()
    subprocess = SubprocessDisplaySerializer(read_only=True, source='subprocess_from')

    def get_transitions(self, obj: Column):
        "Возвращает все id колонок куда возможна  транзакция  с текущей доски"
        # Do NOT use value_list because of prefetch_related!
        return [transition.to_column_id for transition in obj.transitions_from.all()]

    def get_new_cards(self, obj):
        # TODO: Create method which the return new_card
        return []

    class Meta:
        model = Column
        fields = (
            'board',
            'cards',
            'id',
            'subprocess',
            'position',
            'accounts',
            'title',
            'transitions',
            'type',
            'new_cards'
        )


class ColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Column
        fields = (
            'id',
            'type',
            'title',
            'position'
        )


class ColumnWorkflowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Column
        fields = (
            'id',
            'is_end_workflow',
            'is_start_workflow',
            'is_subprocess',
            'title',
            'type',
            'position'
        )


class ColumnStagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Column
        fields = (
            'id',
            'type',
            'title',
            'board',
            'position'
        )


from .subprocess import SubprocessSerializer


class ColumnTransitionSerializer(serializers.ModelSerializer):
    target = SubprocessSerializer(source='subprocess_from', read_only=True)
    transition_on_columns = serializers.SerializerMethodField()

    def get_transition_on_columns(self, obj: Column):
        return ColumnWorkflowSerializer(
            Column.objects.filter(transitions_to__from_column=obj),
            many=True, read_only=True
        ).data

    class Meta:
        model = Column
        fields = (
            'id',
            'is_end_workflow',
            'is_start_workflow',
            'is_subprocess',
            'title',
            'type',
            'position',
            'target',
            'transition_on_columns'
        )


class ColumnWithAccountsSerializer(serializers.ModelSerializer):
    accounts = UserShortSerializer(many=True, read_only=True, source='users')

    class Meta:
        model = Column
        fields = (
            'id',
            'type',
            'title',
            'position',
            'accounts'
        )


class ColumnSubprocessSerializer(serializers.ModelSerializer):
    subprocess = SubprocessSerializer(source='subprocess_from', read_only=True)

    class Meta:
        model = Column
        fields = (
            'id',
            'position',
            'title',
            'type',
            'subprocess'
        )
