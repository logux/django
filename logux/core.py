from abc import abstractmethod, ABC
from typing import List, Callable, Any, Optional

# Logux Response type: https://logux.io/protocols/backend/spec/
# TODO: maybe this is more generic type
LoguxResponse = List[str]


class LoguxCommand(ABC):
    """ Logux Command abstract class.
    All type of Logux Commands should be inheritance from this one.

    Required ony one method `apply()` witch executing command and return LoguxResponse with answer or error message
    """

    @abstractmethod
    def apply(self) -> LoguxResponse:
        raise NotImplemented()


class LoguxAuthCommand(LoguxCommand):
    """ Logux Auth Command provide way to check is the User authenticated.

    The constructor required `cmd_body: List[str]` from Logux Server request and
    `logux_auth(user_id: int, credentials: Any) -> bool` function to prove user is authenticated.

    `logux_auth` function should be injected from consumer app or
    TODO: as default we may user standard Django auth method (sessions) :\
    """

    def __init__(self, cmd_body: List[str], logux_auth: Callable[[int, Any], bool]):
        # meh
        # TODO: validate it
        _, self.user_id, self.credentials, self.auth_id = cmd_body

        # TODO: and check somehow logux_auth function
        self.logux_auth = logux_auth

    def apply(self):
        if self.logux_auth(self.user_id, self.credentials):
            return ['authenticated', self.auth_id]

        return ['denied', self.auth_id]


class LoguxMeta:
    pass


class LoguxActionCommand(LoguxCommand):

    @abstractmethod
    def resend(self, meta: Optional[LoguxMeta]):
        raise NotImplemented

    @abstractmethod
    def access(self, meta: Optional[LoguxMeta]) -> bool:
        raise NotImplemented

    @abstractmethod
    def process(self, meta: Optional[LoguxMeta]) -> None:
        raise NotImplemented
