from typing import Optional, Dict

from django.contrib.auth.models import User

from logux.core import ChannelCommand, Action, Meta
from logux.dispatchers import logux
from logux.exceptions import LoguxProxyException


class UserChannel(ChannelCommand):
    """ Waiting for request like:
    todo: outdated!!!!
    [
      "action",
      { type: 'logux/subscribe', channel: '38/name' },
      { id: "1560954012858 38:Y7bysd:O0ETfc 0", time: 1560954012858 }
    ]

    Should sand back request:

    {
      "version": 1,
      "secret": "secret",
      "commands": [
          [
              "action",
              { type: 'user/name', user: 38, name: 'The User' },
              { clients: ['38:Y7bysd'] }
          ]
      ]
    }

    """
    channel_pattern = r'^users/(?P<user_id>\w+)$'

    def access(self, action: Action, meta: Optional[Meta], headers: Dict) -> bool:
        return self.params['user_id'] == meta.user_id

    def load(self, action: Action, meta: Meta, headers: Dict) -> Action:
        if 'error' in headers:
            raise LoguxProxyException(headers['error'])

        user, _ = User.objects.get_or_create(pk=self.params['user_id'], username='Name')
        return {
            'type': 'users/name',
            'payload': {'userId': str(user.id), 'name': user.first_name}
        }


logux.channels.register(UserChannel)
