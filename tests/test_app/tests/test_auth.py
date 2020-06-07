from django.conf import settings
from django.http import JsonResponse
from django.test import override_settings

from logux.core import AuthCommand
from tests.test_app.tests.helpers import LoguxTestCase, PROTO_VER


class LoguxAuthTestCase(LoguxTestCase):
    """ Auth command """

    good_token = 'good-token'
    good_user_id = '42'

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

    def test_denied_auth(self) -> None:
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


@override_settings(LOGUX_CONFIG={
    **settings.LOGUX_CONFIG,
    'AUTH_FUNC': lambda user_id, token, cookie, headers: cookie['AuthPassword'] == 'good-token'
})
class LoguxAuthWithCookieTestCase(LoguxTestCase):
    """ Auth command with token in the cookies """
    good_token = 'good-token'
    good_user_id = '42'

    def test_success_auth_by_cookie_custom_key_name(self) -> None:
        """ Try to auth by token from the cookie with custom lookup key name. """
        r: JsonResponse = self.logux_request(
            {
                "version": PROTO_VER,
                "secret": "secret",
                "commands": [
                    {
                        "command": "auth",
                        "authId": "gf4Ygi6grYZYDH5Z2BsoR",
                        "userId": "42",
                        "cookie": {
                            "AuthPassword": self.good_token,
                        }
                    }
                ]
            }
        )
        self.assertEqual(r[0]["answer"], AuthCommand.ANSWER.AUTHENTICATED)
        self.assertEqual(r[0]["authId"], 'gf4Ygi6grYZYDH5Z2BsoR')

    def test_fail_auth_by_cookie_custom_key_name(self) -> None:
        """ Try to auth by token from the cookie with wrong lookup key name. """
        r: JsonResponse = self.logux_request(
            {
                "version": PROTO_VER,
                "secret": "secret",
                "commands": [
                    {
                        "command": "auth",
                        "authId": "gf4Ygi6grYZYDH5Z2BsoR",
                        "userId": "42",
                        "cookie": {
                            "token": self.good_token,
                        }
                    }
                ]
            }
        )

        self.assertEqual(r[0]["answer"], AuthCommand.ANSWER.ERROR)
        self.assertEqual(r[0]["authId"], 'gf4Ygi6grYZYDH5Z2BsoR')
        self.assertEqual(r[0]["details"], "missing auth token: 'AuthPassword'")
