from django.apps import AppConfig

from logux import settings
from logux.utils import autodiscover


class LoguxConfig(AppConfig):
    name = 'logux'
    verbose_name = 'Logux'

    def ready(self):
        # import all logux_actions.py and logux_subscriptions.py from consumer modules
        settings.get_config()
        autodiscover()
