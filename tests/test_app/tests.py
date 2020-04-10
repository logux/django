import json
from typing import Dict, Any

from django.conf import settings
from django.http import JsonResponse
from django.test import TestCase
from django.urls import reverse


class LoguxTestCase(TestCase):
    """ TestCase helper. Easy way to make Logux protocol requests """

    def logux_request(self, data: Dict[str, Any]) -> JsonResponse:
        return json.loads(self.client.post(
            path=reverse('logux-dispatch'),
            data=data,
            content_type='application/json'
        ).content.decode('utf-8'))


class ProxyAuthTestCase(LoguxTestCase):
    """ Logux Proxy server and Django backend communication """

    def setUp(self) -> None:
        self.good_token = 'good-token'
        settings.LOGUX_AUTH_FUNC = lambda user_id, token: token == self.good_token

    def test_proxy_auth_good_secret(self) -> None:
        r: JsonResponse = self.logux_request({
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
        })

        self.assertEqual(r[0][0], 'authenticated')
        self.assertEqual(r[0][1], 'gf4Ygi6grYZYDH5Z2BsoR')

    def test_proxy_auth_bad_secret(self) -> None:
        r: JsonResponse = self.logux_request({
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
        })

        self.assertEqual(r[0][0], 'error')
        self.assertEqual(r[0][1], 'Unauthorised Logux proxy server')


class WrongLoguxCommandTypeTestCase(TestCase):
    """ Handling non allowed Logux command types """
    # TODO: first I need figure out: should I raise an exceptions for wrong cmd types
    pass


class LoguxAuthCommandTestCase(LoguxTestCase):
    """ Auth command """

    def setUp(self) -> None:
        self.good_token = 'good-token'
        self.good_user_id = '42'
        settings.LOGUX_AUTH_FUNC = lambda user_id, token: token == self.good_token and user_id == self.good_user_id

    def test_success_auth(self) -> None:
        r: JsonResponse = self.logux_request({
            "version": 2,
            "password": "secret",
            "commands": [
                [
                    "auth",
                    "42",
                    self.good_token,
                    "gf4Ygi6grYZYDH5Z2BsoR"
                ]
            ]
        })

        self.assertEqual(r[0][0], 'authenticated')
        self.assertEqual(r[0][1], 'gf4Ygi6grYZYDH5Z2BsoR')

    def test_denied_auth(self):
        r: JsonResponse = self.logux_request({
            "version": 2,
            "password": "secret",
            "commands": [
                [
                    "auth",
                    "69",
                    "wrong-token",
                    "gf4Ygi6grYZYDH5Z2BsoR"
                ]
            ]
        })

        self.assertEqual(r[0][0], 'denied')
        self.assertEqual(r[0][1], 'gf4Ygi6grYZYDH5Z2BsoR')


class LoguxServerErrorsTestCase(LoguxTestCase):

    def test_unknown_action(self):
        r: JsonResponse = self.logux_request({
            "version": 2,
            "password": "secret",
            "commands": [
                [
                    "action",
                    {
                        "type": "user/unknown",
                        "user": 38,
                        "name": "New"
                    },
                    {
                        "id": "1560954012838 38:Y7bysd:O0ETfc 0",
                        "time": 1560954012838
                    }
                ]
            ]
        })

        self.assertEqual(r[0], ['unknownAction', '1560954012838 38:Y7bysd:O0ETfc 0'])
