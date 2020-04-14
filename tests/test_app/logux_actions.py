from typing import Optional

from django.contrib.auth.models import User

from logux.core import ActionCommand, Meta, LoguxResponse, Action
from logux.dispatchers import actions


class AddCatAction(ActionCommand):
    """ Handler for example from https://logux.io/protocols/backend/examples/

    Request:
        {
          "version": 1,
          "password": "secret",
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

    def resend(self, action: Action, meta: Optional[Meta]) -> LoguxResponse:
        return ['resend', meta.id, {'channels': [f'users/{action["user"]}']}]

    def access(self, action: Action, meta: Optional[Meta]) -> bool:
        # user can rename only himself
        return action['user'] == int(meta.user_id)

    def process(self, action: Action, meta: Optional[Meta]) -> LoguxResponse:
        try:
            user = User.objects.get(pk=action['user'])
            user.first_name = action['name']
            user.save()
        except User.DoesNotExist as err:
            # TODO: waiting for undo implementation
            # self.undo()
            return ['error', meta.id, f'{err}']

        return ['processed', meta.id]


actions.register(AddCatAction)
