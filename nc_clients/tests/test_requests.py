import json

from rest_framework.test import APITestCase, APIClient

from nc_auth.models import User
from ..models import ClientExtraTypeFace


def json_pretty(d: dict) -> str:
    return json.dumps(d, indent=4)


def get_token(client: APIClient, user: dict):
    token = "Token %s" % client.post("/api/v1/auth/handshake/").data["token"]
    resp = client.post(
        "/api/v1/auth/signin/",
        {
            "username": user["email"],
            "password": user["password"]
        },
        format="json",
        HTTP_AUTHORIZATION=token
    ).data
    print(resp)
    return token


class TestClientRequests(APITestCase):
    def setUp(self):
        self.user_credentials = {'email': 'john@snow.com', 'password': 'johnpassword'}
        self.superuser = User.objects.create_superuser(**self.user_credentials)
        self.token = get_token(self.client, self.user_credentials)
        self.headers = {
            "format": "json",
            "HTTP_AUTHORIZATION": self.token,
            "Content-Type": "application/json"
        }

    def test_all(self):
        base_url = lambda url="": "/api/v1/clients/{}".format(url)
        resp = self.client.post(base_url(), {
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
        }, **self.headers)
        self.assertTrue(resp.status_code in {200, 201})

        resp = self.client.post(base_url(), {
            "title": "1234",
            "type_face": "new type",
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
        }, **self.headers)
        self.assertTrue(resp.status_code in {200, 201})

        data = self.client.get(base_url(), **self.headers).data
        print(json_pretty(data))
        id2 = data["results"][1]["id"]

        data = self.client.get(base_url("{}/".format(id2)), **self.headers).data
        print(json_pretty(data))

        resp = self.client.patch(base_url(str(id2) + "/"), {
            "title": "1234_new",
            "type_face": "ip"
        }, **self.headers)
        self.assertTrue(resp.status_code in {200, 201})
        print(json_pretty(resp.data))
        print(ClientExtraTypeFace.objects.all())

        resp = self.client.patch(base_url(str(id2) + "/"), {
            "dataitems": {
                "email": resp.data["dataitems"]["email"],
                "web": [
                    {
                        "data": "http://other.ru"
                    }
                ]
            }
        }, **self.headers)
        self.assertTrue(resp.status_code in {200, 201})
        print(json_pretty(resp.data))
        print(ClientExtraTypeFace.objects.all())
