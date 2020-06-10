class LoguxProxyException(Exception):
    """ Communication errors during acting with Logux Proxy server. """
    pass


class LoguxBadAuthException(Exception):
    """ Wrong AUTH command format or missing keys. """
    pass


class LoguxWrongLoadResultsException(Exception):
    """ load method of ChannelCommand returns invalid data. """
    pass
