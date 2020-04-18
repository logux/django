# Logux Django
Django Logux integration engine https://logux.io/

**Do not use this package until first stable version will be released!**

## Installation

Install from PyPI
```shell script
pip install logux-django
```

Install dev version from current master.
```shell script
pip install -e git://github.com/logux/django.git#egg=logux_django
```

Add `path(r'logux/', include('logux.urls')),` into your `urls.py`

Sets Logux settings in your `settings.py`:
```python
# Logux settings: https://logux.io/guide/starting/proxy-server/
LOGUX_CONTROL_SECRET = "secret"
LOGUX_URL = "http://localhost:31338"
LOGUX_AUTH_FUNC = your_auth_function #  your_auth_function(user_id, token: str) -> bool
```

_Storing passwords or secrets in `settings.py` is bad practice. Use ENV._

For urls and settings examples, please checkout `test_app` 
[settings](https://github.com/logux/django/blob/master/tests/test_project/settings.py)

Keep in mind: the path in your `urls.py` (`logux/`) and the `LOGUX_CONTROL_SECRET` from the settings should be passed 
into [Logux Server](https://logux.io/guide/starting/proxy-server/#creating-the-project) by ENV as 
`LOGUX_BACKEND` and `LOGUX_CONTROL_SECRET` respectively. 

For example: 
```shell script
LOGUX_BACKEND=http://localhost:8000/logux/
LOGUX_CONTROL_SECRET=secret
```

## Usage

### Actions

For `action` handling add `logux_actions.py` file in your app, add `ActionCommand` inheritors and implement all his
abstract methods. 

Actions classes requirements:

* Set `action_type: str`
* Implement all `ActionCommand` abstracts methods
* Implement `resend` and `process` methods if you need (optional)
* import `logux` dispatcher: `from logux.dispatchers import logux`
* Register all your action handlers: `logux.actions.register(YourAction)`

For example – User rename action handler:
```python
from typing import Optional, NoReturn, Dict

from django.contrib.auth.models import User

from logux.core import ActionCommand, Meta, Action
from logux.dispatchers import logux


class RenameUserAction(ActionCommand):
    """ Action Handler for example from https://logux.io/protocols/backend/examples/ """

    action_type = 'user/rename'
    
        def resend(self, action: Action, meta: Optional[Meta]) -> Dict:
            return {'channels': [f'users/{action["user"]}']}
    
        def access(self, action: Action, meta: Meta) -> bool:
            # user can rename only himself
            return action['user'] == int(meta.user_id)
    
        def process(self, action: Action, meta: Optional[Meta]) -> NoReturn:
            user = User.objects.get(pk=action['user'])
            user.first_name = action['name']
            user.save()


logux.actions.register(RenameUserAction)

```

### Channels (Subscription)

For `subsription` handling add `logux_subsriptions.py` file in your app, and `ChannelCommand` inheritors 
and implement all his abstract methods. 

Subscription classes requirements:

* Set `channel_pattern: str` – this is a regexp like Django's url's patters in `urls.py`
* Implement all `ChannelCommand` abstracts methods
* import `logux` dispatcher: `from logux.dispatchers import logux`
* Register all your subscription handlers: `logux.channels.register(YourChannelCommand)`

For example:
```python
from django.contrib.auth.models import User

from logux.core import ChannelCommand, Action, Meta
from logux.dispatchers import logux


class UserChannel(ChannelCommand):
    channel_pattern = r'^user/(?P<user_id>\w+)$'

    def access(self, action: Action, meta: Meta) -> bool:
        return self.params['user_id'] == meta.user_id

    def load(self, action: Action, meta: Meta):
        user = User.objects.get(pk=self.params['user_id'])
        self.send_back(
            {'type': 'user/name', 'user': 38, 'name': user.first_name}
        )


logux.channels.register(UserChannel)

```

For more examples, please checkout `test app` (tests/test_app)

### Utils

#### logux.core.logux_add
`logux_add(action: Action, raw_meta: Optional[Dict] = None) -> NoReturn` is low level API function to send any actions and meta into Logux server.

If `raw_meta` is `None` just empty Dict will be passed to Logux server.

Keep in mind, in the current version `logux_add` is sync.

For more information: https://logux.io/node-api/#log-add

## Development

Create dev environment
```shell script
make venv
make install
make run
```

Type checking and linting:
```shell script
make lint
```

Test:
```shell script
make test
```

## License

The package is available as open source under the terms of the [MIT License](https://opensource.org/licenses/MIT).