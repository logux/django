import logging
from abc import ABC, abstractmethod
from typing import Dict, Union, Type

from logux.core import ActionCommand, ChannelCommand, UnknownAction

logger = logging.getLogger(__name__)


class BaseActionDispatcher(ABC):
    @abstractmethod
    def register(self, action: ActionCommand):
        raise NotImplemented


class DefaultActionDispatcher(BaseActionDispatcher):
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


class DefaultChannelDispatcher(BaseActionDispatcher):
    _subs: Dict[str, ChannelCommand] = {}

    def __str__(self):
        return ', '.join([k for k in self._subs])

    def __getitem__(self, item: str) -> Union[ChannelCommand, Type[UnknownAction]]:
        for sub in self._subs.values():
            if sub.is_match(channel=item):
                return sub

        logger.warning(f"can't match channel name: {item}. tried these URL patterns: "
                       f"{self}")

        # TODO: should it be UnknownSubscription?
        return UnknownAction

    def has_subscription(self, channel_pattern: str) -> bool:
        return channel_pattern in self._subs

    def _sub_is_valid(self, sub) -> bool:
        if not sub.channel_pattern:
            raise ValueError('`action_type` attribute is required for all Actions')

        if self.has_subscription(sub.channel_pattern):
            raise ValueError(f'subscription for channel `{sub.channel_pattern}` already registered')

        if getattr(sub.access, '__isabstractmethod__', False):
            raise ValueError(f'`access` method is required')

        if getattr(sub.load, '__isabstractmethod__', False):
            raise ValueError(f'`load` method is required')

        return True

    def register(self, sub: ChannelCommand):
        if self._sub_is_valid(sub):
            logger.info(f'registering subscription for `{sub.channel_pattern}`')
            self._subs[sub.channel_pattern] = sub


class DefaultDispatcher:
    def __init__(self):
        self.actions = DefaultActionDispatcher()
        self.channels = DefaultChannelDispatcher()


logux = DefaultDispatcher()

__all__ = [logux]
