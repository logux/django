import json
from datetime import datetime
from typing import Dict, Any, Optional

from django.conf import settings
from django.http import JsonResponse
from django.test import TestCase
from django.urls import reverse

from logux.core import ActionCommand, Meta, Action


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


class LoguxActionCommandTestCase(LoguxTestCase):
    def test_property_getters(self):
        """ Tests for Action helpers """

        class TestActionCommand(ActionCommand):

            def access(self, a: Action, m: Optional[Meta]) -> bool:
                return True

        action = TestActionCommand([
            'action',
            {'type': 'user/rename', 'user': 38, 'name': 'New'},
            {'id': "1560954012838 38:Y7bysd:O0ETfc 0", 'time': 1560954012838}
        ])

        self.assertEqual(action.meta.user_id, '38')
        self.assertEqual(action.meta.client_id, '38:Y7bysd')
        self.assertEqual(action.meta.node_id, 'O0ETfc')
        self.assertEqual(action.meta.time, datetime.fromtimestamp(1560954012838 / 1e3))

        action_without_node_id = TestActionCommand([
            'action',
            {'type': 'user/rename', 'user': 38, 'name': 'New'},
            {'id': "1560954012838 38:Y7bysd 0", 'time': 1560954012838}
        ])
        self.assertIsNone(action_without_node_id._meta.node_id)

    def test_meta_cmp(self):
        """ Tests for meta compering """

        # time of m2 gt
        m1 = Meta({'id': '1560954012838 38:Y7bysd:O0ETfc 0', 'time': 1560954012838})  # '2019-06-20 00:20:12.838000'
        m2 = Meta({'id': '1560954012838 38:Y7bysd:O0ETfc 1', 'time': 1560954012848})  # '2019-06-20 00:20:12.848000'

        self.assertTrue(m1 < m2)
        self.assertTrue(m1 != m2)
        self.assertFalse(m1 > m2)
        self.assertFalse(m1 == m2)

        # times is eq, but counter m2 is gt
        m1 = Meta({'id': '1560954012838 38:Y7bysd:O0ETfc 0', 'time': 1560954012838})
        m2 = Meta({'id': '1560954012838 38:Y7bysd:O0ETfc 1', 'time': 1560954012838})

        self.assertTrue(m1 < m2)
        self.assertTrue(m1 != m2)
        self.assertFalse(m1 > m2)
        self.assertFalse(m1 == m2)

        # times is eq, counters is eq, but client_id m2 is gt
        m1 = Meta({'id': '1560954012838 38:Y7bysd:O0ETfc 0', 'time': 1560954012838})
        m2 = Meta({'id': '1560954012838 38:Z7bysd:O0ETfc 0', 'time': 1560954012838})

        self.assertTrue(m1 < m2)
        self.assertTrue(m1 != m2)
        self.assertFalse(m1 > m2)
        self.assertFalse(m1 == m2)

        # m1 and m2 – compactly eq
        m1 = Meta({'id': '1560954012838 38:Y7bysd:O0ETfc 0', 'time': 1560954012838})
        m2 = Meta({'id': '1560954012838 38:Y7bysd:O0ETfc 0', 'time': 1560954012838})

        self.assertFalse(m1 < m2)
        self.assertFalse(m1 != m2)
        self.assertFalse(m1 > m2)
        self.assertTrue(m1 == m2)


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


class LoguxSubscriptionTestCase(LoguxTestCase):
    pass
