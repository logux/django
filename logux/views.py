import json
import logging
from itertools import chain
from typing import List, Tuple, Union

from django.http import JsonResponse, HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from logux import settings
from logux.core import AuthCommand, LoguxValue, UnknownAction, Command, LOGUX_SUBSCRIBE, \
    protocol_version_is_supported
from logux.dispatchers import logux
from logux.exceptions import LoguxProxyException

logger = logging.getLogger(__name__)


class LoguxRequest:
    """ LoguxValue is class for deserialized request from Logux Server proxy

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
        try:
            self._get_body(request)
        except (TypeError, ValueError) as err:
            logger.warning('Wrong body: %s', err)
            raise LoguxProxyException('Wrong body')

        if not protocol_version_is_supported(self.version):
            logger.warning('Unsupported protocol version: %s', self.version)
            raise LoguxProxyException('Back-end protocol version is not supported')

        self.commands: List[Command] = self._parse_commands()

    def _get_body(self, request: HttpRequest):
        _body = json.loads(request.body.decode('utf-8'))

        self.version: int = int(_body['version'])
        self.secret: str = _body['secret']
        self.raw_commands = _body['commands']

    def _parse_commands(self) -> List[Command]:
        commands: List[Command] = []

        for cmd in self.raw_commands:
            cmd_type = cmd['command']

            if cmd_type == self.CommandType.AUTH:
                logger.debug('got auth cmd: %s', cmd)
                commands.append(AuthCommand(cmd, settings.get_config()['AUTH_FUNC']))

            elif cmd_type == self.CommandType.ACTION:
                logger.debug('got action: %s', cmd)
                action_type = cmd['action']['type']

                # subscribe actions
                if action_type == LOGUX_SUBSCRIBE:
                    channel = cmd['action']["channel"]
                    logger.debug('got subscription for channel: %s', channel)
                    commands.append(logux.channels[channel](cmd))
                    continue

                # custom actions
                if not logux.actions.has_action(action_type):
                    logger.warning('unknown action: %s', action_type)
                    commands.append(UnknownAction(cmd))
                    continue

                commands.append(logux.actions[action_type](cmd))

            else:
                logger.warning('wrong command type: %s', cmd)
                err_msg = f'wrong command type: {cmd_type}, expected {self.CommandType.choices}'
                logger.warning(err_msg)
                logger.warning('command with wrong type will be ignored')

        return commands

    def _is_server_authenticated(self) -> bool:
        """ Check Logux proxy server secret """
        return self.secret == settings.get_config()['CONTROL_SECRET']

    def apply_commands(self) -> Tuple[int, Union[str, LoguxValue]]:
        """ Apply all actions commands one by one

        :return: HTTP code and List of command applying results or error message
        """
        if not self._is_server_authenticated():
            # TODO: extract to common way to error response
            err_msg = 'Wrong secret'
            logger.warning(err_msg)
            return 403, err_msg

        if len(self.commands) == 0:
            return 200, [
                {
                    'answer': Command.ANSWER.ERROR,
                    'details': 'command list is empty'
                }
            ]

        return 200, list(filter(None, chain.from_iterable([cmd.apply() for cmd in self.commands])))


@csrf_exempt
@require_http_methods(["POST"])
def dispatch(request: HttpRequest):
    """ Entry point for all requests from Logux Proxy

    :param request: HTTP request from Logux Proxy server.

    :return: JSON response with results of commands applying
    """
    try:
        status, commands_results = LoguxRequest(request).apply_commands()
    except LoguxProxyException as err:
        status, commands_results = (400, str(err))

    if status != 200:
        r = HttpResponse(commands_results)
        r.status_code = status
        return r

    for cmd_res in commands_results:
        logger.debug(cmd_res)

    r = JsonResponse(commands_results, safe=False)
    r.status_code = status
    return r
