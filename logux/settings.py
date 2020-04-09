import logging

from django.conf import settings

# logux server URL
DEFAULT_LOGUX_URL = 'http://localhost:31338'
LOGUX_URL = getattr(settings, 'LOGUX_URL', DEFAULT_LOGUX_URL)

# TODO: add into DOC: do not store your pass in settings.py, use ENV instead
LOGUX_CONTROL_SECRET = getattr(settings, 'LOGUX_CONTROL_SECRET', None)

if LOGUX_CONTROL_SECRET is None:
    raise ValueError("can't get LOGUX_CONTROL_PASSWORD")

# TODO: don't like it. bt for now let's say consumer should implement auth func by himself
LOGUX_AUTH_FUNC = getattr(settings, 'LOGUX_AUTH_FUNC', None)

if LOGUX_AUTH_FUNC is None:
    # TODO: add link to doc
    raise ValueError('LOGUX_AUTH_FUNC is required! Set auth function in your settings.py')

DEBUG = getattr(settings, 'DEBUG', True)

if DEBUG:
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
