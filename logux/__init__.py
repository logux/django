"""
    Django Logux integration engine: https://logux.io
"""
__title__ = 'Django Logux integration engine'
__version__ = "2.0.0rc3"
__author__ = 'Vadim Iskuchekov @egregors'
__license__ = 'MIT License'

# Synonyms
VERSION = __version__
AUTHOR = __author__

# Logux protocol version: https://logux.io/protocols/ws/spec/
LOGUX_PROTOCOL_VERSION = 4

default_app_config = 'logux.apps.LoguxConfig'
