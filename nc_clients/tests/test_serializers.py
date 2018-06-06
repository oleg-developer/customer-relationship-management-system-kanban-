import json

from django.contrib.auth import get_user_model
from django.test import TestCase

from nc_clients.models import *
from nc_clients.serializers import ClientDetailedSerializer


class TestClientSerializer(TestCase):
    TEST_DATA = {
        "title": "1234",
        "type_face": "ip",
        "inn": 12463423,
        "dataitems": {
            "email": [
                {
                    "data": "2@2.ru"
                }
            ],
            "web": [
                {
                    "data": "http://1234.ru"
                }
            ]
        }
    }

    def setUp(self):
        User = get_user_model()
        self.user = User(email="1@1.ru")
        self.user.save()
        Client.objects.all().delete()

    def test_save(self):
        ser = ClientDetailedSerializer(data=self.TEST_DATA)
        ser.is_valid(raise_exception=True)
        client = ser.save(user_created=self.user)
        self.assertEqual(Client.objects.get(title="1234").data_items.count(), 2)

    def test_serialize(self):
        self.test_save()
        client = Client.objects.get(title="1234")
        data = ClientDetailedSerializer(client).data
        print(json.dumps(data, indent=4))
        self.assertEqual(data['dataitems']['email'][0]['data'], self.TEST_DATA['dataitems']['email'][0]['data'])
