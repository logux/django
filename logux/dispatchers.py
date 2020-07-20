import logging
from abc import ABC, abstractmethod
from typing import Dict, Union, Type

from logux.core import ActionCommand, ChannelCommand, UnknownAction, UnknownSubscription

logger = logging.getLogger(__name__)


class BaseActionDispatcher(ABC):
    """ Meta class for all Dispatchers """

    @abstractmethod
    def register(self, action: ActionCommand):
        """ Add Action handler for Dispatcher """
        raise NotImplementedError()


class DefaultActionDispatcher(BaseActionDispatcher):
    """ Default logux Dispatcher for Actions """
    _actions: Dict[str, Type[ActionCommand]] = {}

    def __str__(self):
        return ', '.join(self._actions)

    def __getitem__(self, action_type: str):
        return self._actions[action_type]

    def _action_is_valid(self, action: Type[ActionCommand]) -> bool:
        if not action.action_type:
            raise ValueError('`action_type` attribute is required for all Actions')

        if self.has_action(action.action_type):
            raise ValueError(f'`{action.action_type}` action type already registered')

        if getattr(action.access, '__isabstractmethod__', False):
            raise ValueError('`access` method is required')

        return True

    def has_action(self, action_type: str) -> bool:
        """ Check if Dispatcher has handler for particular action type """
        return action_type in self._actions

    def register(self, action: Type[ActionCommand]):  # type: ignore # noqa
        if self._action_is_valid(action):
            logger.info('registering action `%s`', action.action_type)
            self._actions[action.action_type] = action


class DefaultChannelDispatcher(BaseActionDispatcher):
    """ Default logux Dispatcher for Channels """
    _subs: Dict[str, Type[ChannelCommand]] = {}

    def __str__(self):
        return ', '.join(self._subs)

    def __getitem__(self, item: str) -> Union[Type[ChannelCommand], Type[UnknownAction]]:
        for sub in self._subs.values():
            if sub.is_match(channel=item):
                return sub

        logger.warning("can't match channel name: %s", item)

        return UnknownSubscription

    def has_subscription(self, channel_pattern: str) -> bool:
        """ Check if Dispatcher has handler for a particular channel subscription type """
        return channel_pattern in self._subs

    def _sub_is_valid(self, sub) -> bool:
        if not sub.channel_pattern:
            raise ValueError('`action_type` attribute is required for all Actions')

        if self.has_subscription(sub.channel_pattern):
            raise ValueError(f'subscription for channel `{sub.channel_pattern}` already registered')

        if getattr(sub.access, '__isabstractmethod__', False):
            raise ValueError('`access` method is required')

        if getattr(sub.load, '__isabstractmethod__', False):
            raise ValueError('`load` method is required')

        return True

    def register(self, action: Type[ChannelCommand]):  # type: ignore # noqa
        if self._sub_is_valid(action) and action.channel_pattern is not None:
            logger.info('registering subscription for `%s`', action.channel_pattern)
            self._subs[action.channel_pattern] = action


class DefaultDispatcher:
    """ Shortcut for actions and channels Dispatchers """

    def __init__(self):
        self.actions = DefaultActionDispatcher()
        self.channels = DefaultChannelDispatcher()


logux = DefaultDispatcher()

__all__ = ['logux']
