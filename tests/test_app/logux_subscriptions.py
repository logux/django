from typing import Optional

from logux.core import ChannelCommand, Action, Meta
from logux.dispatchers import logux
from logux.exceptions import LoguxProxyException
from tests.test_app.models import User


class UserChannel(ChannelCommand):
    """ TODO: add docstring """
    channel_pattern = r'^users/(?P<user_id>\w+)$'

    def access(self, action: Action, meta: Optional[Meta]) -> bool:
        return self.params['user_id'] == meta.user_id

    def load(self, action: Action, meta: Meta) -> Action:
        if 'error' in self.headers:
            raise LoguxProxyException(self.headers['error'])

        user, _ = User.objects.get_or_create(id=self.params['user_id'], username='Name')
        return {
            'type': 'users/name',
            'payload': {'userId': str(user.id), 'name': user.username}
        }


logux.channels.register(UserChannel)
