import json
from pathlib import Path
from typing import List

from django.db import models
from rest_framework.response import Response
from rest_framework.views import APIView

from nc_auth.permissions import IsAuthenticated
from nc_clients.models import Client
from nc_core.utils import memcached_method, get_field_type, FieldRegex


class ClientMeta(APIView):
    permission_classes = (IsAuthenticated,)

    @staticmethod
    def _field_map_fn(field: models.Field):
        return {
            "name": field.name,
            "label": str(field.verbose_name),
            "type": get_field_type(field),
            "pattern": FieldRegex(field).regex
        }

    def build_meta(self, fields: List[str]):
        meta = Client._meta
        fields = list(map(lambda field: self._field_map_fn(meta.get_field(field)), fields))
        return fields

    @memcached_method(key="ClientMetaConfig", timeout=60 * 5)
    def load_config(self):
        file = (Path(__file__) / ".." / ".." / "client_forms.json").resolve().open()
        config = json.load(file)
        return {
            client_type: self.build_meta(data["fields"])
            for client_type, data in config.items()
        }

    def get(self, request, client_type):
        config = self.load_config()
        return Response(config.get(client_type, config[""]))
