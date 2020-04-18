from typing import Optional, Dict

from django.contrib.auth.models import User

from logux.core import ActionCommand, Meta, Action
from logux.dispatchers import logux


class RenameUserAction(ActionCommand):
    """ Handler for example from https://logux.io/protocols/backend/examples/

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
    action_type = 'user/rename'

    def resend(self, action: Action, meta: Optional[Meta]) -> Dict:
        return {'channels': [f'users/{action["user"]}']}

    def access(self, action: Action, meta: Meta) -> bool:
        # user can rename only himself
        return action['user'] == int(meta.user_id)

    def process(self, action: Action, meta: Optional[Meta]) -> None:
        user = User.objects.get(pk=action['user'])
        user.first_name = action['name']
        user.save()


logux.actions.register(RenameUserAction)
