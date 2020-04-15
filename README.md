# logux-django
Django Logux integration engine https://logux.io/

**Do not use this package until first stable version will be released!**

## Install like pkg
From PyPI – not ready yet
From git (master): 
```
python3 -m venv env
source env/bin/activate
pip install -e git://github.com/logux/django.git#egg=logux
```

Add `path(r'logux/', include('logux.urls')),` into your `urls.py`

Add `ActionCommand` inheritors into `logux_actions.py` inside any of your module
Add `SubscriptionCommand` inheritors into `logux_subcriptions.py` inside any of your module

Checkout test app for examples (tests/test_app)

## Development

```
make venv
make install
make run
```