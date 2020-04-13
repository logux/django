import logging
from abc import ABC, abstractmethod
from typing import Dict

from logux.core import ActionCommand

logger = logging.getLogger(__name__)


class BaseActionDispatcher(ABC):
    @abstractmethod
    def register(self, action: ActionCommand):
        raise NotImplemented


class DefaultActionDispatcher(BaseActionDispatcher):
    """ TODO: add Doc String """
    _actions: Dict[str, ActionCommand] = {}

    def __str__(self):
        return ', '.join([k for k in self._actions])

    def __getitem__(self, action_type: str):
        return self._actions[action_type]

    def _action_is_valid(self, action: ActionCommand) -> bool:
        if not action.action_type:
            raise ValueError('`action_type` attribute is required for all Actions')

        if self.has_action(action.action_type):
            raise ValueError(f'`{action.action_type}` action type already registered')

        if getattr(action.access, '__isabstractmethod__', False):
            raise ValueError(f'`access` method is required')

        return True

    def has_action(self, action_type: str) -> bool:
        return action_type in self._actions

    def register(self, action: ActionCommand):
        if self._action_is_valid(action):
            logger.info(f'registering action `{action.action_type}`')
            self._actions[action.action_type] = action


# TODO: maybe rename? maybe all actions and all subscriptions need be here? 🤔🤔🤔
#  looks like, subscriptions are almost the same as actions.
actions = DefaultActionDispatcher()

__all__ = ['actions']
