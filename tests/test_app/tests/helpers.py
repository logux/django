import json
from typing import Dict, Any

from django.http import JsonResponse
from django.test import TestCase
from django.urls import reverse


class LoguxTestCase(TestCase):
    """ TestCase helper. Easy way to make Logux protocol requests """

    def logux_request(self, data: Dict[str, Any]) -> JsonResponse:
        """ Logux request shortcut """
        return json.loads(self.client.post(
            path=reverse('logux-dispatch'),
            data=data,
            content_type='application/json'
        ).content.decode('utf-8'))
