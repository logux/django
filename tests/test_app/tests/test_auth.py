from django.conf import settings
from django.http import JsonResponse

from tests.test_app.tests.helpers import LoguxTestCase


class LoguxAuthCommandTestCase(LoguxTestCase):
    """ Auth command """

    def setUp(self) -> None:
        self.good_token = 'good-token'
        self.good_user_id = '42'
        settings.LOGUX_AUTH_FUNC = lambda user_id, token: token == self.good_token and user_id == self.good_user_id

    def test_success_auth(self) -> None:
        r: JsonResponse = self.logux_request({
            "version": 3,
            "secret": "secret",
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
            "version": 3,
            "secret": "secret",
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
