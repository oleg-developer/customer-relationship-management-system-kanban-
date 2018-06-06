from typing import List

from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers
from rest_framework.utils import model_meta

from nc_core.models import dataitems
from nc_core.serializers.dataitems import DataItems
from nc_core.serializers.utils import ReverseBooleanField
from nc_modules.models import Module
from ..models import User


class UserAvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('logo',)


class UserShortSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='first_name')
    logo_url = serializers.FileField(source='logo')
    is_admin = serializers.BooleanField(source="is_company_owner", read_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'name',
            'short_name',
            'full_name',
            'is_admin',
            'logo_url'
        )


class UserModulePermissions(serializers.Field):
    def to_representation(self, relation):
        modules = {module.id for module in Module.objects.get_for_user(relation.instance)}
        return {module.name: module.id in modules for module in Module.objects.get_all()}

    def to_internal_value(self, data: dict) -> List[Module]:
        return [Module.objects.get_by_name(module) for module, v in data.items() if v]


class UserDetailSerializer(serializers.ModelSerializer):
    logo_url = serializers.FileField(source='logo', read_only=True)
    info = serializers.CharField(max_length=1024, source='notes', required=False, allow_blank=True)
    password = serializers.CharField(max_length=128, required=False, allow_blank=True, write_only=True)
    username = serializers.CharField(read_only=True, source="email")
    is_locked = ReverseBooleanField(source="is_active")
    is_admin = serializers.BooleanField(source="is_company_owner", read_only=True)

    storage_rights = UserModulePermissions(source="module_permissions")
    dataitems = DataItems(required=False, source="data_items")

    @transaction.atomic()
    def create(self, validated_data: dict) -> User:
        request_user = self.context['request'].user

        email_item = next(filter(lambda item: isinstance(item, dataitems.Email), validated_data['data_items']), None)
        password = validated_data.pop("password", None)
        data_items = validated_data.pop("data_items", None)

        if not email_item:
            raise serializers.ValidationError("'email' is required")
        if not password:
            raise serializers.ValidationError("'password' is required")

        user = get_user_model().objects.create_user(email_item.data, password)
        validated_data['company'] = request_user.company
        for attr, value in validated_data.items():
            setattr(user, attr, value)
        user.save()

        # user = super(UserDetailSerializer, self).create({"user": user, **validated_data})

        if data_items is not None:
            user.data_items.set(data_items)

        return user

    @transaction.atomic()
    def update(self, user: User, validated_data: dict) -> User:
        password = validated_data.pop('password', None)
        info = model_meta.get_field_info(user)
        for attr, value in validated_data.items():
            if attr in info.relations:
                field = getattr(user, attr)
                if info.relations[attr].to_many:
                    field.set(value)
                elif isinstance(value, dict):
                    for subattr, subvalue in value.items():
                        setattr(field, subattr, subvalue)
                    field.save()
            else:
                setattr(user, attr, value)
        user.save()

        if password:
            user.user.set_password(password)
        Module.objects.get_for_user.clear_cache(user)
        return user

    class Meta:
        model = User
        fields = (
            "id",
            "info", "birthday", "logo_url", "position",
            "full_name", "first_name", "middle_name", "last_name",
            "username", "password",
            "storage_rights", "is_locked", "is_admin",
            "dataitems"
        )
        read_only_fields = (
            "id",
            "logo_url",
            "full_name",
            "is_admin",
        )
