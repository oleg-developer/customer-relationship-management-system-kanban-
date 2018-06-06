from rest_framework import serializers

from nc_clients.models import Client
from ..models import Card


class CardDetailSerializer(serializers.ModelSerializer):
    client_id = serializers.PrimaryKeyRelatedField(source="client", queryset=Client.objects.all(),
                                                   required=False, allow_null=True)
    client_name = serializers.StringRelatedField(source="client", read_only=True)
    is_last_position = serializers.BooleanField(source="is_last", read_only=True)

    board_id = serializers.SerializerMethodField()

    def get_board_id(self, card: Card):
        return card.column.board_id if card.column else None

    class Meta:
        model = Card
        fields = (
            "id", "color", "is_last_position", "position", "title", "blocked",
            # "slug_id",
            "board_id", "column", "client_id", "client_name",
            "created", "deleted", "user_created", "user_modified",
            "archive_date", "basket_date", "status"
        )
        read_only_fields = (
            "is_last_position", "blocked",
            "board_id", "client_name",
            "created", "deleted", "user_created", "user_modified",
            "archive_date", "basket_date", "status"
        )
