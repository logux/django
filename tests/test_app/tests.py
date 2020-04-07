import json

from django.http import JsonResponse
from django.test import TestCase
from django.urls import reverse

from logux import settings


class ProxyAuthTestCase(TestCase):
    """ Testing Logux Proxy server and Django backend communication """

    def setUp(self) -> None:
        self.good_token = 'good-token'
        settings.LOGUX_AUTH_FUNC = lambda user_id, token: token == self.good_token

    def test_proxy_auth_good_secret(self) -> None:
        r: JsonResponse = json.loads(self.client.post(
            path=reverse('logux-dispatch'),
            data={
                "version": 2,
                "password": "secret",
                "commands": [
                    [
                        "auth",
                        "38",
                        "good-token",
                        "gf4Ygi6grYZYDH5Z2BsoR"
                    ]
                ]
            },
            content_type='application/json'
        ).content.decode('utf-8'))

        self.assertEqual(r[0][0], 'authenticated')
        self.assertEqual(r[0][1], 'gf4Ygi6grYZYDH5Z2BsoR')

    def test_proxy_auth_bad_secret(self) -> None:
        r: JsonResponse = json.loads(self.client.post(
            path=reverse('logux-dispatch'),
            data={
                "version": 2,
                "password": "wrong-secret",
                "commands": [
                    [
                        "auth",
                        "38",
                        "good-token",
                        "gf4Ygi6grYZYDH5Z2BsoR"
                    ]
                ]
            },
            content_type='application/json'
        ).content.decode('utf-8'))

        self.assertEqual(r[0][0], 'error')
        self.assertEqual(r[0][1], 'Unauthorised Logux proxy server')
