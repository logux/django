from typing import Optional

from logux.core import ActionCommand, Meta, LoguxResponse
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

    def resend(self, meta: Optional[Meta]) -> LoguxResponse:
        return ['resend', meta['id'], {'channels': [f'users/{self.action_context["user"]}']}]

    def access(self, meta: Optional[Meta]) -> bool:
        print(self.action_context['user'])
        return True if self.action_context['user'] == 38 else False

    def process(self, meta: Optional[Meta]) -> LoguxResponse:
        # doing some staff
        # ...
        # TODO: add here real model update with Exceptions handling
        return ['processed', meta['id']]


actions.register(AddCatAction)
