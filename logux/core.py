import logging
from abc import abstractmethod, ABC
from datetime import datetime
from typing import List, Callable, Optional, Dict

# Logux Response type: https://logux.io/protocols/backend/spec/
# TODO: add examples from spec
LoguxResponse = LoguxRequest = List[str]
ActionContext = Meta = Dict[str, str]
logger = logging.getLogger(__name__)


class Command(ABC):
    """ Logux Command abstract class.
    All type of Logux Commands should be inheritance from this one.

    Required ony one method `apply()` witch executing command and return LoguxResponse with answer or error message
    """

    @abstractmethod
    def apply(self) -> LoguxResponse:
        raise NotImplemented()


class AuthCommand(Command):
    """ Logux Auth Command provide way to check is the User authenticated.

    The constructor required `cmd_body: List[str]` from Logux Server request and
    `logux_auth(user_id: int, credentials: Any) -> bool` function to prove user is authenticated.

        `cmd_body` example: ["auth", "38", "good-token", "gf4Ygi6grYZYDH5Z2BsoR"]

    `logux_auth` function should be injected from consumer app or
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

    def add(self) -> None:
        # https://github.com/logux/django/issues/12
        raise NotImplemented()


class ActionCommand(Command):
    """
        TODO:
         - [ ] add Doc string
         - [ ] add meta helpers
    """
    # Required field, if the `action_type` property does not defined DefaultActionDispatcher will raise
    #  ValueError('`action_type` attribute is required for all Actions') Exception
    action_type: Optional[str] = None

    # TODO: add helpers into self
    #  user_id, client_id, node_id, time(datatime),
    #  date_diff (https://github.com/logux/core/blob/master/is-first-older/index.js) ???
    #  send_back, undo.

    def __init__(self, cmd_body: List[ActionContext]):
        """ cmd_body should looks like:
            [
              "action",                                                         // action_type
              { type: 'user/rename', user: 38, name: 'New' },                   // cmd_body[1]
              { id: "1560954012838 38:Y7bysd:O0ETfc 0", time: 1560954012838 }   // cmd_body[2]
            ]
        """
        self.action: ActionContext = cmd_body[1]
        self.meta: Meta = cmd_body[2]

    # Helpers
    @property
    def _uid(self):
        return self.meta['id'].split(' ')[1].split(':')

    @property
    def user_id(self) -> str:
        """ Get user id from mata.id.
         For example, if meta.id is '1560954012838 38:Y7bysd:O0ETfc 0',
         then user_id is '38'
         """
        return self._uid[0]

    @property
    def client_id(self) -> str:
        """ Get client id from mata.id.
         For example, if meta.id is '1560954012838 38:Y7bysd:O0ETfc 0',
         then client_id is '38:Y7bysd'
         """
        return ':'.join(self._uid[:2])

    @property
    def node_id(self) -> Optional[str]:
        """ Get node id from mata.id if exist.
         For example, if meta.id is '1560954012838 38:Y7bysd:O0ETfc 0',
         then client_id is 'O0ETfc'

         If UID does not contain node_id None will be returned
         """
        return self._uid[-1] if len(self._uid) == 3 else None

    @property
    def time(self) -> datetime:
        """
        Get time from mata in Python datetime type.
         For example, if meta is {'id': "1560954012838 38:Y7bysd 0", 'time': 1560954012838},
         then time is 'datetime.datetime(2019, 6, 20, 0, 20, 12, 838000)'
        """
        return datetime.fromtimestamp(int(self.meta['time']) / 1e3)

    @property
    def date_diff(self):
        pass

    def send_back(self):
        pass

    def undo(self):
        pass

    # Required and optional action methods
    def _finally(self) -> LoguxResponse:  # noqa
        # TODO: rewrite
        """ Callback which will be run on the end of action/subscription processing or on an error """
        return []

    def apply(self) -> List[LoguxResponse]:
        # https://github.com/logux/django/issues/5
        return [
            self.resend(self.meta),
            ["approved", self.meta['id']] if self.access(self.meta) else ['denied', self.meta['id']],
            self.process(self.meta) if self.access(self.meta) else [],
            self._finally()
        ]

    @abstractmethod
    def access(self, meta: Optional[Meta]) -> bool:
        """ TODO: add docs """
        raise NotImplemented()

    def resend(self, meta: Optional[Meta]) -> LoguxResponse:
        """ TODO: add docs """
        return []

    def process(self, meta: Optional[Meta]) -> LoguxResponse:
        """ TODO: add docs """
        return []


class UnknownAction(ActionCommand):
    """ Action for generation `unknownAction` error.
    Will be used and evaluated if actions dispatcher
    got unexpected action type """

    def access(self, meta: Optional[Meta]) -> bool:
        return False

    def apply(self) -> List[LoguxResponse]:
        return [['unknownAction', self.meta['id']]]
