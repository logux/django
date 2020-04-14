from typing import Optional

from django.contrib.auth.models import User

from logux.core import SubscriptionCommand, Action, Meta
from logux.dispatchers import subscriptions


class UserSubscription(SubscriptionCommand):
    """ Waiting for request like:

    [
      "action",
      { type: 'logux/subscribe', channel: '38/name' },
      { id: "1560954012858 38:Y7bysd:O0ETfc 0", time: 1560954012858 }
    ]

    """
    channel_pattern = r'^user/(?P<user_id>\w+)$'

    def load(self, action: Action, meta: Meta):
        # TODO: send_back
        #   {
        #       "version": 1,
        #       "password": "secret",
        #       "commands": [
        #           [
        #               "action",
        #               { type: 'user/name', user: 38, name: 'The User' },
        #               { clients: ['38:Y7bysd'] }
        #           ]
        #       ]
        #   }

        # should fail with DoesNotExist, and eval undo
        user = User.objects.get(pk=self.params['user_id'])

        # should send back { type: 'user/name', user: 38, name: 'The User' },
        # and here into meta will be added id and time from original subscription
        # action
        # TODO: is it correct?
        self.send_back(
            {'type': 'user/name', 'user': 38, 'name': user.first_name}
        )

        return ['processed', self.meta.id]

    def access(self, action: Action, meta: Optional[Meta]) -> bool:
        return self.params['user_id'] == meta.user_id


subscriptions.register(UserSubscription)
