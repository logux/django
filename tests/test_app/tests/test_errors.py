from django.http import JsonResponse

from tests.test_app.tests.helpers import LoguxTestCase, PROTO_VER


class LoguxServerErrorsTestCase(LoguxTestCase):
    """ Check error formats """

    def test_unknown_action(self):
        """ unknownAction """
        r: JsonResponse = self.logux_request({
            "version": PROTO_VER,
            "secret": "secret",
            "commands": [
                {
                    "command": "action",
                    "action": {
                        "type": "user/unknown",
                        "user": 38,
                        "name": "New"
                    },
                    "meta": {
                        "id": "1560954012838 38:Y7bysd:O0ETfc 0",
                        "time": 1560954012838
                    }
                }
            ]
        })

        self.assertEqual(r[0]['answer'], 'unknownAction', )
        self.assertEqual(r[0]['id'], '1560954012838 38:Y7bysd:O0ETfc 0')
