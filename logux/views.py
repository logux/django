import json
import logging
from itertools import chain
from typing import List, Iterable

from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt

from logux import settings
from logux.core import Command, AuthCommand, LoguxResponse
from logux.dispatchers import actions
from logux.settings import LOGUX_CONTROL_SECRET

logger = logging.getLogger(__name__)


class LoguxRequest:
    """ LoguxRequest is class for deserialized request from Logux Server proxy

    The constructor should extract common fields like `version` and `password` and parse list of commands.

    By default command parser will provide only AuthCommand implementation (with logux_auth function
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
        self._body = json.loads(request.body.decode('utf-8'))

        # TODO: what should I do with the versions?
        self.version: str = self._body['version']
        self.password: str = self._body['password']
        self.commands: List[Command] = self._parse_commands()

    def _parse_commands(self) -> List[Command]:
        commands: List[Command] = []

        for cmd in self._body['commands']:
            cmd_type = cmd[0]

            if cmd_type == self.CommandType.AUTH:
                logger.debug(f'got auth cmd: {cmd}')
                commands.append(AuthCommand(cmd, settings.LOGUX_AUTH_FUNC))

            elif cmd_type == self.CommandType.ACTION:
                logger.debug(f'got action: {cmd}')
                action_type = cmd[1]['type']

                if not actions.has_action(action_type):
                    logger.error(f'wrong action type: {action_type}')
                    continue

                commands.append(actions[action_type](cmd))

            else:
                logger.error(f'wrong command type: {cmd}')
                err_msg = f'wrong command type: {cmd_type}, expected {[c_type for c_type in self.CommandType.choices]}'
                logger.error(err_msg)
                logger.warning(f'command with wrong type will be ignored')

        return commands

    def _is_server_authenticated(self) -> bool:
        """ Check Logux proxy server password """
        return self._body['password'] == LOGUX_CONTROL_SECRET

    def apply_commands(self) -> Iterable[LoguxResponse]:
        if not self._is_server_authenticated():
            # TODO: extract to common way to error response
            err_msg = 'Unauthorised Logux proxy server'
            logger.warning(err_msg)
            return [['error', err_msg]]

        if len(self.commands) == 0:
            return [['error', f'command list is empty']]

        return filter(None, chain.from_iterable([cmd.apply() for cmd in self.commands]))


@csrf_exempt
def dispatch(request: HttpRequest):
    """
        TODO: if ["auth", string|bool userId, string token, string authId] why userId is bool?
    """
    commands_results = list(LoguxRequest(request).apply_commands())
    for cmd_res in commands_results:
        logger.debug(cmd_res)

    return JsonResponse(commands_results, safe=False)
