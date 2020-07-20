from typing import Optional, Dict, List

from django.contrib.auth.models import User

from logux.core import ActionCommand, Meta, Action
from logux.dispatchers import logux
from logux.exceptions import LoguxProxyException


class RenameUserAction(ActionCommand):
    """ TODO: this
    """
    action_type = 'users/name'

    def resend(self, action: Action, meta: Optional[Meta], headers: Dict) -> List[str]:
        return [f"users/{action['payload']['userId']}"]

    def access(self, action: Action, meta: Meta, headers: Dict) -> bool:
        if 'error' in headers:
            raise LoguxProxyException(headers['error'])
        return action['payload']['userId'] == meta.user_id

    def process(self, action: Action, meta: Meta, headers: Dict) -> None:
        user = User.objects.get(pk=action['payload']['userId'])
        user.first_name = action['payload']['name']
        user.save()


class CleanUserAction(ActionCommand):
    """ On users/clean action set all names to "" and sends users/name action with new name to all clients """
    action_type = 'users/clean'

    def access(self, action: Action, meta: Meta, headers: Dict) -> bool:
        if 'error' in headers:
            raise LoguxProxyException(headers['error'])
        return True

    def process(self, action: Action, meta: Meta, headers: Dict) -> None:
        for u in User.objects.all():
            u.first_name = ''
            u.save()
            self.send_back({
                'type': 'users/name',
                'payload':
                    {
                        'userId': str(u.id),
                        'name': str(u.first_name)
                    }
            })


logux.actions.register(RenameUserAction)
logux.actions.register(CleanUserAction)
