from typing import Optional, Dict

from django.contrib.auth.models import User

from logux.core import ChannelCommand, Action, Meta
from logux.dispatchers import logux


class UserChannel(ChannelCommand):
    """ Waiting for request like:

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

    def load(self, action: Action, meta: Meta) -> Action:
        user = User.objects.get(pk=self.params['user_id'])
        return {'type': 'users/name', 'user': 38, 'name': user.first_name}


logux.channels.register(UserChannel)
