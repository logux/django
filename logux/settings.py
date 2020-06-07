import logging

from django.conf import settings

CONFIG_DEFAULTS = {
    'URL': 'http://localhost:31337',
    'CONTROL_SECRET': None,
    'AUTH_FUNC': None
}

DEBUG = getattr(settings, 'DEBUG', True)

if DEBUG:
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


# TODO: find a way how to cache it for prod and do not cache it for tests
# @lru_cache()
def get_config():
    """ Get default configs and marge it with a user's config """
    USER_CONFIG = getattr(settings, "LOGUX_CONFIG", {})
    CONFIG = CONFIG_DEFAULTS.copy()
    CONFIG.update(USER_CONFIG)

    if CONFIG['CONTROL_SECRET'] is None:
        raise ValueError("can't get CONTROL_SECRET")

    if CONFIG['AUTH_FUNC'] is None:
        raise ValueError('AUTH_FUNC is required! Set auth function in your settings.py')

    return CONFIG
