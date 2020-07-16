from typing import Optional, Dict, List

from django.contrib.auth.models import User

from logux.core import ActionCommand, Meta, Action
from logux.dispatchers import logux
from logux.exceptions import LoguxProxyException


class RenameUserAction(ActionCommand):
    """ Handler for example from https://logux.io/protocols/backend/examples/
    todo: outdated!!!
    Request:
        {
          "version": 1,
          "secret": "secret",
          "commands": [
            [
              "action",
              { type: 'user/rename', user: 38, name: 'New' },
              { id: "1560954012838 38:Y7bysd:O0ETfc 0", time: 1560954012838 }
            ],
            [
              "action",
              { type: 'user/rename', user: 21, name: 'New' },
              { id: "1560954012900 38:Y7bysd:O0ETfc 1", time: 1560954012900 }
            ]
          ]
        }

    Response:
        [
          ["resend", "1560954012838 38:Y7bysd:O0ETfc 0", { "channels": ["users/38"] }],
          ["resend", "1560954012900 38:Y7bysd:O0ETfc 1", { "channels": ["users/21"] }],
          ["approved", "1560954012838 38:Y7bysd:O0ETfc 0"],
          ["denied", "1560954012900 38:Y7bysd:O0ETfc 1"],
          ["processed", "1560954012838 38:Y7bysd:O0ETfc 0"]
        ]

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


logux.actions.register(RenameUserAction)
