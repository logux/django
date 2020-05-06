from django.utils.module_loading import autodiscover_modules

_autodiscovered = False


def autodiscover():
    """
    Auto-discover INSTALLED_APPS logux_actions.py modules and fail silently
    when not present. This forces an import on them to register any logux bits
    they may want.
    """
    global _autodiscovered  # pylint: disable=global-statement

    if _autodiscovered:
        return

    autodiscover_modules('logux_actions', 'logux_subscriptions')
    _autodiscovered = True
