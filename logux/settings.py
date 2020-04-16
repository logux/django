import logging

from django.conf import settings

from logux.utils import autodiscover

# logux server URL
DEFAULT_LOGUX_URL = 'http://localhost:31337'
LOGUX_URL = getattr(settings, 'LOGUX_URL', DEFAULT_LOGUX_URL)

LOGUX_CONTROL_SECRET = getattr(settings, 'LOGUX_CONTROL_SECRET', None)

if LOGUX_CONTROL_SECRET is None:
    raise ValueError("can't get LOGUX_CONTROL_PASSWORD")

LOGUX_AUTH_FUNC = getattr(settings, 'LOGUX_AUTH_FUNC', None)

if LOGUX_AUTH_FUNC is None:
    raise ValueError('LOGUX_AUTH_FUNC is required! Set auth function in your settings.py')

DEBUG = getattr(settings, 'DEBUG', True)

if DEBUG:
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# import all logux_actions.py and logux_subscriptions.py from consumer modules
autodiscover()
