from typing import Dict

from django.db import transaction
from rest_framework import serializers
from rest_framework.utils import model_meta

from nc_core.serializers.dataitems import DataItems
from ..models import *


class TypeFace(serializers.Field):
    def __init__(self, **kwargs):
        kwargs['source'] = "*"
        super().__init__(**kwargs)

    def to_representation(self, client: Client) -> str:
        return client.get_type_face()

    def to_internal_value(self, data: str) -> Dict[str, str]:
        return {"type_face": data}


# ================================================================================

class EmployeeSerializer(serializers.ModelSerializer):
    dataitems = DataItems(required=False, source="data_items")

    @transaction.atomic()
    def create(self, validated_data: dict) -> Employee:
        data_items = validated_data.pop("data_items")
        emp = Employee(**validated_data)
        emp.save()
        emp.data_items.set(data_items)
        return emp

    @transaction.atomic()
    def update(self, emp: Employee, validated_data: dict) -> Employee:
        data_items = validated_data.pop("data_items", None)
        info = model_meta.get_field_info(emp)
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                field = getattr(emp, attr)
                field.set(value)
            else:
                setattr(emp, attr, value)
        emp.save()

        if data_items is not None:
            emp.data_items.set(data_items)
        return emp

    class Meta:
        model = Employee
        fields = "__all__"
        read_only_fields = (
            "owner", "user_created", "user_modified", "created", "modified"
        )


# ================================================================================

class ClientSerializer(serializers.ModelSerializer):
    # READ ONLY
    type_face = TypeFace(read_only=True)

    def create(self, validated_data):
        raise NotImplementedError("ClientSerializer::create")

    def update(self, instance, validated_data):
        raise NotImplementedError("ClientSerializer::update")

    class Meta:
        model = Client
        fields = ("id", "title", "more_info", "type_face", "group", "tag", "address")


class ClientDetailedSerializer(serializers.ModelSerializer):
    REQUIRED_TOGETHER = {
        Client.FACE_CHOICES.PHYS: (),
        Client.FACE_CHOICES.IP: (),
        None: ()
    }

    type_face = TypeFace(required=True)
    dataitems = DataItems(required=False, source="data_items")
    employees = EmployeeSerializer(many=True, read_only=True, source="employee_set")
    relations = ClientSerializer(many=True, read_only=True)

    def validate(self, attrs: dict) -> dict:
        type_face = attrs.get("type_face")
        required = self.REQUIRED_TOGETHER.get(type_face, self.REQUIRED_TOGETHER[None])
        for k in required:
            if not attrs.get(k, None):
                raise serializers.ValidationError("Field '{}' is required".format(k))
        return attrs

    @transaction.atomic()
    def create(self, validated_data: dict) -> Client:
        type_face = validated_data.pop("type_face")
        data_items = validated_data.pop("data_items")
        client = Client(**validated_data)
        client.set_type_face(type_face, getattr(self.context.get('request', None), 'user', None))
        client.save()
        client.data_items.set(data_items)
        return client

    @transaction.atomic()
    def update(self, client: Client, validated_data: dict) -> Client:
        type_face = validated_data.pop("type_face", None)
        data_items = validated_data.pop("data_items", None)

        info = model_meta.get_field_info(client)
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                field = getattr(client, attr)
                field.set(value)
            else:
                setattr(client, attr, value)

        if type_face is not None:
            client.set_type_face(type_face, getattr(self.context.get('request', None), 'user', None))
        client.save()

        if data_items is not None:
            client.data_items.set(data_items)
        return client

    class Meta:
        model = Client
        exclude = ("_type_face", "_extra_type_face")
        read_only_fields = (
            "group", "tag", "relations", "owner", "user_created", "user_modified", "created", "modified"
        )


# ================================================================================

class GroupSerializer(serializers.ModelSerializer):
    counter = serializers.IntegerField(read_only=True)

    class Meta:
        model = Group
        fields = ("id", "name", "description", "counter")


class GroupDetailedSerializer(GroupSerializer):
    clients_list = ClientSerializer(many=True, read_only=True, source="client_set")

    class Meta(GroupSerializer.Meta):
        fields = ("id", "name", "description", "counter", "clients_list")


# ================================================================================

class TagSerializer(serializers.ModelSerializer):
    counter = serializers.IntegerField(read_only=True)
    hex = serializers.CharField(max_length=6, allow_blank=True, source="color")

    def get_counter(self, tag: Tag) -> int:
        return tag.client_set.count()

    class Meta:
        model = Tag
        fields = ("id", "title", "hex", "counter")
