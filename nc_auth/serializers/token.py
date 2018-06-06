from rest_framework import serializers

from nc_auth.models import Token


class TokenSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        return {'token': instance.key}

    class Meta:
        model = Token
        fields = (
            'key', 'client', 'version', 'platform'
        )
