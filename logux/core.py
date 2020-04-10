import logging
from abc import abstractmethod, ABC
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


class ActionCommand(Command):
    """
        TODO:
         - [ ] add Doc string
         - [ ] add meta helpers
    """
    # Required field, if the `action_type` property does not defined DefaultActionDispatcher will raise
    #  ValueError('`action_type` attribute is required for all Actions') Exception
    action_type: Optional[str] = None

    def __init__(self, cmd_body: List[ActionContext]):
        """ cmd_body should looks like:
            [
              "action",                                                         // action_type
              { type: 'user/rename', user: 38, name: 'New' },                   // cmd_body[1]
              { id: "1560954012838 38:Y7bysd:O0ETfc 0", time: 1560954012838 }   // cmd_body[2]
            ]
        """
        self.action_context: ActionContext = cmd_body[1]
        self.meta: Meta = cmd_body[2]

    # noinspection PyMethodMayBeStatic
    def _finally(self) -> LoguxResponse:
        # TODO: Add doc's: why you may need this method?
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
