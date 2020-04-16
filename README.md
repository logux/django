# logux-django
Django Logux integration engine https://logux.io/

**Do not use this package until first stable version will be released!**

## Installation

Install using pip (dev version).
```
pip install -e git://github.com/logux/django.git#egg=logux_django
```

Add `path(r'logux/', include('logux.urls')),` into your `urls.py`

Sets Logux settings in your  `settings.py`:
```
# Logux settings: https://logux.io/guide/starting/proxy-server/
LOGUX_CONTROL_SECRET = "secret"
LOGUX_URL = "http://localhost:31338"
LOGUX_AUTH_FUNC = your_auth_function #  your_auth_function(user_id, token: str) -> bool
```

For urls and settings examples, please checkout `test_app` [settings](https://github.com/logux/django/blob/master/tests/test_project/settings.py)

Keep in mind: the path in your `urls.py` (`logux/`) and the `LOGUX_CONTROL_SECRET` from the settings should be passed into [Logux Server](https://logux.io/guide/starting/proxy-server/#creating-the-project) by ENV as 
`LOGUX_BACKEND` and `LOGUX_CONTROL_SECRET` respectively. 

For example: 
```
LOGUX_BACKEND=http://localhost:8000/logux/
LOGUX_CONTROL_SECRET=secret
```

## Usage

### Actions

For `action` handling add `logux_actions.py` file in your app, and implement `ActionCommand` inheritors. 

Actions classes requirements:

* Set `action_type: str`
* Implement all `ActionCommand` abstracts methods
* Implement `resend` and `process` methods (optional)
* import `logux` dispatcher: `from logux.dispatchers import logux`
* Register all your action handlers: `logux.actions.register(YourAction)`

For example – User rename action handler:
```
from typing import Optional

from django.contrib.auth.models import User

from logux.core import ActionCommand, Meta, LoguxResponse, Action
from logux.dispatchers import logux


class RenameUserAction(ActionCommand):
    """ Action Handler for example from https://logux.io/protocols/backend/examples/ """

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
                self.undo(
                    meta,
                    reason='user does not exist',
                    extra={'original_exception': f'{err}'}
                )
                return ['error', meta.id, f'{err}']

            return ['processed', meta.id]

logux.actions.register(RenameUserAction)

```

### Subscription

For `subsription` handling add `logux_subsriptions.py` file in your app, and implement `ChannelCommand` inheritors. 

Subscription classes requirements:

* Set `channel_pattern: str` – this is a regexp like Django's url's patters in `urls.py`
* Implement all `ChannelCommand` abstracts methods
* import `logux` dispatcher: `from logux.dispatchers import logux`
* Register all your subscription handlers: `logux.subscriptions.register(YourSubscription)`

For example:
```
from typing import Optional

from django.contrib.auth.models import User

from logux.core import ChannelCommand, Action, Meta
from logux.dispatchers import logux


class UserChannel(ChannelCommand):
    """ Subscription Handler for example from https://logux.io/protocols/backend/examples/ """

    channel_pattern = r'^user/(?P<user_id>\w+)$'

    def load(self, action: Action, meta: Meta):
        try:
            user = User.objects.get(pk=self.params['user_id'])
        except User.DoesNotExist as err:
            self.undo(meta, 'user does not exist', {'original_exception': f'{err}'})
            return ['processed', self.meta.id]

        self.send_back(
            {'type': 'user/name', 'user': 38, 'name': user.first_name}
        )

        return ['processed', self.meta.id]

    def access(self, action: Action, meta: Optional[Meta]) -> bool:
        return self.params['user_id'] == meta.user_id


logux.subscriptions.register(UserChannel)

```

For more examples, please checkout `test app` (tests/test_app)

## Development

Create dev environment
```
make venv
make install
make run
```

Test:
```
make test
```

## License

The package is available as open source under the terms of the [MIT License](https://opensource.org/licenses/MIT).