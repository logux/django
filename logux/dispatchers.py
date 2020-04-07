from abc import ABC, abstractmethod
from typing import Dict

from logux.core import LoguxActionCommand


class BaseActionDispatcher(ABC):
    @abstractmethod
    def register(self, type_: str, action: LoguxActionCommand):
        raise NotImplemented


class DefaultActionDispatcher(BaseActionDispatcher):
    """ TODO: add Doc String """
    _actions: Dict[LoguxActionCommand] = {}

    def register(self, type_: str, action: LoguxActionCommand):
        pass


# TODO: should be a Singleton
actions = DefaultActionDispatcher()

__all__ = ['actions']
