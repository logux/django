import json
import logging
from typing import List

from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt

from logux import settings
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

    class CommandType:
        """ All possible Logux command types.
        https://logux.io/protocols/backend/spec/#requests """
        AUTH = 'auth'
        ACTION = 'action'

        choices = [AUTH, ACTION]

    def __init__(self, request: HttpRequest):
        if not request.body:
            raise ValueError("wrong request body")

        self._body = json.loads(request.body.decode('utf-8'))

        # TODO: what should I do with the versions?
        self.version: str = self._body['version']
        self.password: str = self._body['password']
        self.commands: List[LoguxCommand] = self._parse_commands()

    def _parse_commands(self) -> List[LoguxCommand]:
        commands: List[LoguxCommand] = []

        # TODO: rewrite it though dynamic dispatching
        for cmd in self._body['commands']:
            cmd_type = cmd[0]

            if cmd_type == self.CommandType.AUTH:
                logger.debug(f'got auth cmd: {cmd}')
                commands.append(LoguxAuthCommand(cmd, settings.LOGUX_AUTH_FUNC))

            elif cmd_type == self.CommandType.ACTION:
                # TODO: inject consumers dict with all actions
                logger.debug(f'got action: {cmd}')
                raise NotImplemented()

            else:
                logger.error(f'wrong command type: {cmd}')
                err_msg = f'wrong command type: {cmd_type}, expected {[c_type for c_type in self.CommandType.choices]}'
                logger.error(err_msg)
                logger.warning(f'command with wrong type will be ignored')
                # TODO: should I raise exception here?
                # raise ValueError(err_msg)

        return commands

    def _is_server_authenticated(self) -> bool:
        """ Check Logux proxy server password """
        return self._body['password'] == LOGUX_CONTROL_PASSWORD

    def apply_commands(self) -> List[LoguxResponse]:
        if not self._is_server_authenticated():
            # TODO: i should extract each cmd and eval them separately
            # TODO: more informative messages
            # TODO: extract to common way to error response
            err_msg = 'Unauthorised Logux proxy server'
            logger.warning(err_msg)
            return [['error', err_msg]]

        if len(self.commands) == 0:
            return [['error', f'command list is empty']]

        return [cmd.apply() for cmd in self.commands]


# TODO: what we should do with session and csrf token?
@csrf_exempt
def dispatch(request: HttpRequest):
    """
        TODO: if ["auth", string|bool userId, string token, string authId] why userId is bool?
    """
    return JsonResponse(LoguxRequest(request).apply_commands(), safe=False)
