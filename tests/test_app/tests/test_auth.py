from django.conf import settings
from django.http import JsonResponse

from logux.core import AuthCommand
from tests.test_app.tests.helpers import LoguxTestCase, PROTO_VER


class LoguxAuthCommandTestCase(LoguxTestCase):
    """ Auth command """

    def setUp(self) -> None:
        self.good_token = 'good-token'
        self.good_user_id = '42'
        settings.LOGUX_AUTH_FUNC = lambda user_id, token: token == self.good_token and user_id == self.good_user_id

    def test_success_auth(self) -> None:
        """ Try to auth with:

            * token in body
            * token in cookie
        """
        # token in body
        r: JsonResponse = self.logux_request({
            "version": PROTO_VER,
            "secret": "secret",
            "commands": [
                {
                    "command": "auth",
                    "authId": "gf4Ygi6grYZYDH5Z2BsoR",
                    "userId": "42",
                    "token": self.good_token,
                }
            ]
        })

        self.assertEqual(r[0]["answer"], AuthCommand.ANSWER.AUTHENTICATED)
        self.assertEqual(r[0]["authId"], 'gf4Ygi6grYZYDH5Z2BsoR')

        # token in cookie
        r = self.logux_request({
            "version": PROTO_VER,
            "secret": "secret",
            "commands": [
                {
                    "command": "auth",
                    "authId": "gf4Ygi6grYZYDH5Z2BsoR",
                    "userId": "42",
                    "cookie": {
                        "token": self.good_token
                    },
                }
            ]
        })

        self.assertEqual(r[0]["answer"], AuthCommand.ANSWER.AUTHENTICATED)
        self.assertEqual(r[0]["authId"], 'gf4Ygi6grYZYDH5Z2BsoR')

    def test_denied_auth(self):
        """ Check denied auth.

            * bad token
            * bad token in cookie
            * missing token
        """
        # bad token
        r: JsonResponse = self.logux_request({
            "version": PROTO_VER,
            "secret": "secret",
            "commands": [
                {
                    "command": "auth",
                    "authId": "gf4Ygi6grYZYDH5Z2BsoR",
                    "userId": "42",
                    "token": "blablabla",
                }
            ]
        })

        self.assertEqual(r[0]["answer"], AuthCommand.ANSWER.DENIED)
        self.assertEqual(r[0]["authId"], 'gf4Ygi6grYZYDH5Z2BsoR')

        # bad token in cookie
        r = self.logux_request({
            "version": PROTO_VER,
            "secret": "secret",
            "commands": [
                {
                    "command": "auth",
                    "authId": "gf4Ygi6grYZYDH5Z2BsoR",
                    "userId": "42",
                    "cookie": {
                        "token": "blablabla"
                    }
                }
            ]
        })

        self.assertEqual(r[0]["answer"], AuthCommand.ANSWER.DENIED)
        self.assertEqual(r[0]["authId"], 'gf4Ygi6grYZYDH5Z2BsoR')

        # missing token
        r = self.logux_request({
            "version": PROTO_VER,
            "secret": "secret",
            "commands": [
                {
                    "command": "auth",
                    "authId": "gf4Ygi6grYZYDH5Z2BsoR",
                    "userId": "42"
                }
            ]
        })

        self.assertEqual(r[0]["answer"], AuthCommand.ANSWER.ERROR)
        self.assertEqual(r[0]["authId"], 'gf4Ygi6grYZYDH5Z2BsoR')
        self.assertEqual(r[0]["details"], "missing auth token: 'token'")
