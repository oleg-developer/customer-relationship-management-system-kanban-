from rest_framework import serializers


class ReverseBooleanField(serializers.BooleanField):
    def to_internal_value(self, data: bool):
        return not super(ReverseBooleanField, self).to_internal_value(data)

    def to_representation(self, value):
        return not super(ReverseBooleanField, self).to_representation(value)
