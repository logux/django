import json
import logging
from typing import List

from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt

from logux.core import LoguxCommand, LoguxAuthCommand, LoguxResponse
from logux.settings import LOGUX_CONTROL_PASSWORD

logger = logging.getLogger(__name__)


class LoguxRequest:
    """ LoguxRequest is class for deserialized request from Logux Server proxy

    The constructor should extract common fields like `version` and `password` and parse list of commands.

    By default command parser will provide only LoguxAuthCommand implementation (with logux_auth function
    injection). Other Action should by parsed by consumer dispatcher.

    TODO: add ref to doc's and examples of consumer dispatcher in the test app
    """

    def __init__(self, request: HttpRequest):
        if not request.body:
            raise ValueError("wrong request body")

        self._body = json.loads(request.body.decode('utf-8'))

        self.version: str = self._body['version']
        self.password: str = self._body['password']
        self.commands: List[LoguxCommand] = self._parse_commands()

    def _parse_commands(self) -> List[LoguxCommand]:
        commands: List[LoguxCommand] = []

        # TODO: rewrite it though dynamic dispatching
        for cmd in self._body['commands']:
            if cmd[0] == 'auth':
                # TODO: inject logux auth func from consumer app
                commands.append(LoguxAuthCommand(cmd, lambda user_id, token: True))
            elif cmd[0] == 'action':
                # TODO: inject consumers dict with all actions
                raise NotImplemented()
            else:
                raise ValueError(f'wrong command type: {cmd[0]}, expected "auth" or "action"')

        return commands

    def _is_server_authenticated(self) -> bool:
        """ Check Logux proxy server password """
        return self._body['password'] == LOGUX_CONTROL_PASSWORD

    def apply_commands(self) -> List[LoguxResponse]:
        if not self._is_server_authenticated():
            # TODO: more informative messages
            # TODO: should I answer 200 or 401?
            # TODO: extract to common way to error response
            err_msg = 'Unauthorised Logux proxy server'
            logger.warning(err_msg)
            return [['error', err_msg]]
        return [cmd.apply() for cmd in self.commands]


# TODO: what we should do with session and csrf token?
@csrf_exempt
def dispatch(request: HttpRequest):
    """
    {
        "version": 2,
        "password": "secret",
        "commands": [
            ["auth", false, null, "BJ9InmfJre3FfJGKC5-sy"]
        ]
    }
    TODO: if ["auth", string userId, any credentials, string authId] why userId is bool?
    """
    return JsonResponse(LoguxRequest(request).apply_commands(), safe=False)
