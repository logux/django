from django.http import JsonResponse

from tests.test_app.tests.helpers import LoguxTestCase


class LoguxServerErrorsTestCase(LoguxTestCase):

    def test_unknown_action(self):
        r: JsonResponse = self.logux_request({
            "version": 3,
            "secret": "secret",
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
