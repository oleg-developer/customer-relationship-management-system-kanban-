from typing import Dict, List, Any, Generator

from polymorphic.query import PolymorphicQuerySet
from rest_framework import serializers

from nc_core.models.dataitems import DataItem
from ..models import dataitems

DATAITEMS_TYPES = {
    "address": dataitems.Address,
    "phone": dataitems.PhoneNumber,
    "email": dataitems.Email,
    "web": dataitems.WebSite,
}


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = dataitems.Address
        fields = ("id", "data")


class PhoneNumberSerializer(serializers.ModelSerializer):
    number = serializers.CharField(max_length=128, required=True, allow_blank=False)
    extra_code = serializers.CharField(max_length=50, required=False, allow_blank=True, source="data")

    class Meta:
        model = dataitems.PhoneNumber
        fields = ("id", "number", "extra_code")


class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = dataitems.Email
        fields = ("id", "data")


class WebSiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = dataitems.WebSite
        fields = ("id", "data")


CLS_MAPPING = {
    dataitems.Address: AddressSerializer,
    dataitems.PhoneNumber: PhoneNumberSerializer,
    dataitems.Email: EmailSerializer,
    dataitems.WebSite: WebSiteSerializer,
}


class DataItems(serializers.Field):
    REPR_TYPE = Dict[str, List[Dict[str, Any]]]

    def to_representation(self, data_items: PolymorphicQuerySet) -> REPR_TYPE:
        return {
            k: CLS_MAPPING[cls](data_items.instance_of(cls), many=True).data
            for k, cls in DATAITEMS_TYPES.items()
        }

    def _to_internal_value_gen(self, data: REPR_TYPE) -> Generator[DataItem, None, None]:
        for k, values in data.items():
            cls = DATAITEMS_TYPES.get(k, None)
            if not cls:
                raise serializers.ValidationError("Wrong DataItem type '{}'".format(k))
            serializer_cls = CLS_MAPPING[cls]
            for value in values:
                if "id" in value and (value["id"] or value["id"] == 0):
                    serializer = serializer_cls(cls.objects.get(id=value["id"]), data=value)
                else:
                    serializer = serializer_cls(data=value)
                if serializer.is_valid():
                    yield serializer.save()

    def to_internal_value(self, data: dict) -> List[DataItem]:
        return list(self._to_internal_value_gen(data))
