from __future__ import annotations

import json
import logging
import re
from abc import abstractmethod, ABC
from copy import deepcopy
from datetime import datetime
from typing import List, Callable, Optional, Dict

import requests
from django.conf import settings

LoguxResponse = LoguxRequest = List[str]
Action = Dict[str, str]
logger = logging.getLogger(__name__)

# https://logux.io/protocols/backend/examples/#subscription
LOGUX_SUBSCRIBE = 'logux/subscribe'


class Meta:
    """ Logux meta: https://logux.io/guide/concepts/meta/
    TODO: add docs about comp:
        https://github.com/logux/django/issues/12#issuecomment-612394901

    TODO: Comparing method implements according Node API:
      https://github.com/logux/core/blob/master/is-first-older/index.js
    """

    def __init__(self, raw_meta: Dict[str, str]):
        # Take raw meta and parse all required to properties
        self._raw_meta = raw_meta
        # Keep in mind, if self._raw_meta will change all properties do not be reassignment,
        #   so, do not change self._raw_meta during Meta instance lifecycle

        self._uid: List[str] = self._get_uid()

        self.id: str = self._raw_meta['id']

        self.user_id: str = self._get_user_id()
        self.client_id: str = self._get_client_id()
        self.node_id: str = self._get_node_id()
        self.time: datetime = self._get_time()

    def __getitem__(self, item):
        return self._raw_meta[item]

    def __eq__(self, o: Meta) -> bool:
        return self.time == o.time

    def __ne__(self, o: Meta) -> bool:
        return self.time != o.time

    def __lt__(self, other: Meta) -> bool:
        return self.time < other.time

    def __le__(self, other: Meta) -> bool:
        return self.time <= other.time

    def __gt__(self, other: Meta) -> bool:
        return self.time > other.time

    def __ge__(self, other: Meta) -> bool:
        return self.time >= other.time

    # Helpers
    def _get_uid(self):
        try:
            uid = self._raw_meta['id'].split(' ')[1].split(':')
        except IndexError:
            raise ValueError(f'wrong meta id format: {self._raw_meta["id"]}')
        return uid

    def _get_user_id(self) -> str:
        """ Get user id from mata.id.
         For example, if meta.id is '1560954012838 38:Y7bysd:O0ETfc 0',
         then user_id is '38'
         """
        return self._uid[0]

    def _get_client_id(self) -> str:
        """ Get client id from mata.id.
         For example, if meta.id is '1560954012838 38:Y7bysd:O0ETfc 0',
         then client_id is '38:Y7bysd'
         """
        return ':'.join(self._uid[:2])

    def _get_node_id(self) -> Optional[str]:
        """ Get node id from mata.id if exist.
         For example, if meta.id is '1560954012838 38:Y7bysd:O0ETfc 0',
         then client_id is 'O0ETfc'

         If UID does not contain node_id None will be returned
         """
        return self._uid[-1] if len(self._uid) == 3 else None

    def _get_time(self) -> datetime:
        """
        Get time from mata in Python datetime type.
         For example, if meta is {'id': "1560954012838 38:Y7bysd 0", 'time': 1560954012838},
         then time is 'datetime.datetime(2019, 6, 20, 0, 20, 12, 838000)'
        """
        return datetime.fromtimestamp(int(self._raw_meta['time']) / 1e3)

    def get_raw_meta(self) -> Dict:
        return deepcopy(self._raw_meta)

    def get_json(self) -> str:
        return json.dumps(self._raw_meta)  # , ensure_ascii=False).encode('utf8')


class Command(ABC):
    """ Logux Command abstract class.
    All type of Logux Commands should be inheritance from this one.

    Required ony one method `apply()` witch executing command and return LoguxResponse with answer or error message
    """

    @abstractmethod
    def apply(self) -> LoguxResponse:
        raise NotImplemented()

    @staticmethod
    def add(action: Dict, meta: Optional[Meta] = None) -> None:
        # https://logux.io/node-api/#log-add
        # https://github.com/logux/core/blob/36c604158b49697790e96c6e6919c22752e231cb/log/index.js#L29
        #
        # The doc's says:
        #   It will set id, time (if they was missed) and added property to meta and call all listeners.
        # Where we should take id and time? Should we generate it somehow, or it is always meta from already
        # existed action?

        if meta is None:
            # TODO: deal with meta generating
            raise ValueError('for now meta is required!')

        data = {
            # TODO: deal with versions
            "version": 2,
            "password": settings.LOGUX_CONTROL_SECRET,
            "commands": [
                ["action",
                 action,
                 meta.get_raw_meta()]
            ]
        }

        # TODO: clean up this mess. catch all possible errors, and add some logs messages
        logger.debug(f'add action {action} with meta {meta.get_raw_meta()} to Log')
        try:
            r = requests.post(url=settings.LOGUX_URL, json=data)
            logger.debug(f'response: {r.text}')
            if r.status_code != 200:
                # TODO: just write it in the log
                raise ValueError(f'Bad Request to Logux (add): {r.text}')
        except ConnectionError as err:
            pass

    def get_meta(self) -> Optional[Meta]:
        if isinstance(self, (ActionCommand,)):
            return self.meta

        return None


class AuthCommand(Command):
    """ Logux Auth Command provide way to check is the User authenticated.

    The constructor required `cmd_body: List[str]` from Logux Server request and
    `logux_auth(user_id: int, credentials: Any) -> bool` function to prove user is authenticated.

        `cmd_body` example: ["auth", "38", "good-token", "gf4Ygi6grYZYDH5Z2BsoR"]

    `logux_auth` function should be injected from consumer app or

    TODO: this class should be ActionCommand probably
    """

    def __init__(self, cmd_body: LoguxRequest, logux_auth: Callable[[str, str], bool]):
        # meh
        # TODO: validate it
        _, self.user_id, self.token, self.auth_id = cmd_body

        # TODO: and check somehow logux_auth function
        self.logux_auth = logux_auth

    def apply(self) -> List[LoguxResponse]:
        # TODO: probably need LoguxResponse constructor
        return [['authenticated', self.auth_id]] \
            if self.logux_auth(self.user_id, self.token) \
            else [['denied', self.auth_id]]


class ActionCommand(Command):
    """
        TODO:
         - [ ] add Doc string
         - [x] add meta helpers
    """
    # Required field, if the `action_type` property does not defined DefaultActionDispatcher will raise
    #  ValueError('`action_type` attribute is required for all Actions') Exception
    action_type: Optional[str] = None

    # TODO: add helpers into self
    #  user_id, client_id, node_id, time(datatime),
    #  date_diff (https://github.com/logux/core/blob/master/is-first-older/index.js) ???
    #  send_back, undo.

    def __init__(self, cmd_body: List[Action]):
        """ cmd_body should looks like:
            [
              "action",                                                         // action_type
              { type: 'user/rename', user: 38, name: 'New' },                   // cmd_body[1]
              { id: "1560954012838 38:Y7bysd:O0ETfc 0", time: 1560954012838 }   // cmd_body[2]
            ]
        """
        self._action: Action = cmd_body[1]
        self._meta: Meta = Meta(cmd_body[2])

    @property
    def action(self):
        # do not change internal action state from outside
        return deepcopy(self._action)

    @property
    def meta(self):
        # do not change internal meta state from outside
        return deepcopy(self._meta)

    def send_back(self, action: Action, raw_meta: Optional[Dict] = None):
        # if `raw_meta` contain `id`, `time` or `clients` the original data will be overwritten
        raw_meta = {} if raw_meta is None else raw_meta
        meta = Meta(
            {
                'id': self.meta.id,
                'time': self._meta['time'],
                'clients': [self.meta.client_id],
                **raw_meta
            }
        )
        self.add(action, meta)

    def undo(self):
        raise NotImplemented()

    # Required and optional action methods (this methods should be implemented by consumer
    def _finally(self) -> LoguxResponse:  # noqa
        # TODO: rewrite
        """ Callback which will be run on the end of action/subscription processing or on an error """
        return []

    @abstractmethod
    def access(self, action: Action, meta: Optional[Meta]) -> bool:
        """ TODO: add docs """
        raise NotImplemented()

    def resend(self, action: Action, meta: Optional[Meta]) -> LoguxResponse:
        """ TODO: add docs """
        return []

    def process(self, action: Action, meta: Optional[Meta]) -> LoguxResponse:
        """ TODO: add docs """
        return []

    # Required for Command
    def apply(self) -> List[LoguxResponse]:
        # https://github.com/logux/django/issues/5
        # TODO: do not eval access few times
        return [
            self.resend(self._action, self._meta),
            ["approved", self._meta.id] if self.access(self._action, self._meta) else ['denied', self._meta.id],
            self.process(self._action, self._meta) if self.access(self._action, self._meta) else [],
            self._finally()
        ]


class SubscriptionCommand(ActionCommand):
    """ Todo: add docs: https://logux.io/protocols/backend/examples/#subscription

    This class looks exactly like ActionCommand, but with few additional features.
    So, maybe it may be a Mixin

    [
      "action",
      { type: 'logux/subscribe', channel: '38/name' },
      { id: "1560954012858 38:Y7bysd:O0ETfc 0", time: 1560954012858 }
    ]

    """
    # Required field, if the `channel_pattern` property does not defined DefaultSubscriptionsDispatcher will raise
    #  ValueError('`channel_pattern` attribute is required for `logux/subscription` Actions') Exception
    action_type = LOGUX_SUBSCRIBE
    channel_pattern: Optional[str] = None

    def __init__(self, cmd_body: List[Action]):
        super().__init__(cmd_body)
        self.channel = cmd_body[1]['channel']
        self.params = self._parse_params()

    def _parse_params(self) -> Dict:
        return re.match(self.channel_pattern, self.channel).groupdict()

    @classmethod
    def is_match(cls, channel: str) -> bool:
        return True if re.match(cls.channel_pattern, channel) else None

    @abstractmethod
    def load(self, action: Action, meta: Meta):
        pass

    def apply(self) -> List[LoguxResponse]:
        # TODO: do not eval access few times
        return [
            ["approved", self._meta.id] if self.access(self._action, self._meta) else ['denied', self._meta.id],
            self.load(self._action, self._meta) if self.access(self._action, self._meta) else []
        ]


class UnknownAction(ActionCommand):
    """ Action for generation `unknownAction` error.
    Will be used and evaluated if actions dispatcher
    got unexpected action type """

    def access(self, action: Action, meta: Optional[Meta]) -> bool:
        return False

    def apply(self) -> List[LoguxResponse]:
        return [['unknownAction', self._meta.id]]
