from django.apps import AppConfig

from logux import settings
from logux.utils import autodiscover


class LoguxConfig(AppConfig):
    """ Logux app conf """
    name = 'logux'
    verbose_name = 'Logux'

    def ready(self):
        # check if all required settings is defined
        settings.get_config()
        # import all logux_actions.py and logux_subscriptions.py from consumer modules
        autodiscover()
