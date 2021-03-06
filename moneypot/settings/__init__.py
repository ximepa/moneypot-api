""" Settings for callcenter """


class LocalSettingsException(Exception):
    pass


from .base import *

try:
    from .local import *
except ImportError as exc:
    raise LocalSettingsException('%s (did you rename settings/local-dist.py?)' % exc.args[0])
