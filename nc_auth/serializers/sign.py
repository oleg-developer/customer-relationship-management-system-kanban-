from django.contrib.auth.hashers import check_password
from django.utils.translation import ugettext as _
from rest_framework import serializers


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=128)
    password = serializers.CharField(min_length=3, max_length=64)

    class Meta:
        fields = ('email', 'password')


class ChangePasswordSerializer(serializers.Serializer):
    old_pass = serializers.CharField(min_length=3)
    new_pass = serializers.CharField(min_length=3)

    def validate(self, attrs):
        if check_password(attrs['old_pass'], self.context['request'].user.password):
            return {'new_pass': attrs['new_pass']}
        else:
            raise serializers.ValidationError(_("an incorrect password was entered"))


class SigninSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(min_length=3)
