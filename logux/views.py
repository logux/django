import json
import logging
from itertools import chain
from typing import List, Iterable

from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt

from logux import settings
from logux.core import AuthCommand, LoguxResponse, UnknownAction, Command, LOGUX_SUBSCRIBE, \
    protocol_version_is_supported
from logux.dispatchers import logux
from logux.settings import LOGUX_CONTROL_SECRET

logger = logging.getLogger(__name__)


class LoguxRequest:
    """ LoguxRequest is class for deserialized request from Logux Server proxy

    The constructor should extract common fields like `version` and `secret` and parse list of commands.

    By default, command parser will provide only AuthCommand implementation (with logux_auth function
    injection). Other Action should by parsed by consumer dispatcher.

    TODO: send 403 if proxy secret is wrong
    TODO: send 429 if brute force check is fail
    """

    class CommandType:
        """ All possible Logux command types.
        https://logux.io/protocols/backend/spec/#requests """
        AUTH = 'auth'
        ACTION = 'action'

        choices = [AUTH, ACTION]

    def __init__(self, request: HttpRequest):
        """ Construct the Command and check protocol version support.

        :param request: request with command from Logux Proxy
        :raises: base Exception if request protocol version is not supported by backend
        """
        self._body = json.loads(request.body.decode('utf-8'))

        self.version: int = int(self._body['version'])
        # TODO: should I crush App here?
        if not protocol_version_is_supported(self.version):
            # TODO: extract to custom logux exception
            raise Exception(f'Unsupported protocol version: {self.version}')

        self.secret: str = self._body['secret']
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

                # subscribe actions
                if action_type == LOGUX_SUBSCRIBE:
                    channel = cmd[1]["channel"]
                    logger.debug(f'got subscription for channel: {channel}')
                    commands.append(logux.channels[channel](cmd))
                    continue

                # custom actions
                if not logux.actions.has_action(action_type):
                    logger.error(f'unknown action: {action_type}')
                    commands.append(UnknownAction(cmd))
                    continue

                commands.append(logux.actions[action_type](cmd))

            else:
                logger.error(f'wrong command type: {cmd}')
                err_msg = f'wrong command type: {cmd_type}, expected {[c_type for c_type in self.CommandType.choices]}'
                logger.error(err_msg)
                logger.warning(f'command with wrong type will be ignored')

        return commands

    def _is_server_authenticated(self) -> bool:
        """ Check Logux proxy server secret """
        return self._body['secret'] == LOGUX_CONTROL_SECRET

    def apply_commands(self) -> Iterable[LoguxResponse]:
        if not self._is_server_authenticated():
            # TODO: extract to common way to error response
            err_msg = 'Unauthorised Logux proxy server'
            logger.warning(err_msg)
            return [['error', {}, err_msg]]

        if len(self.commands) == 0:
            return [['error', {}, f'command list is empty']]

        return filter(None, chain.from_iterable([cmd.apply() for cmd in self.commands]))


@csrf_exempt
def dispatch(request: HttpRequest):
    """ Entry point for all requests from Logux Proxy

    :param request: HTTP request from Logux Proxy server.

    :return: JSON response with results of commands applying
    """
    commands_results = list(LoguxRequest(request).apply_commands())
    for cmd_res in commands_results:
        logger.debug(cmd_res)

    return JsonResponse(commands_results, safe=False)
