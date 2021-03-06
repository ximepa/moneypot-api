# -*- encoding: utf-8 -*-
from __future__ import print_function, division, unicode_literals, absolute_import

import os

from . import base
import sys


# To extend any settings from settings/base.py here's an example.
# If you don't need to extend any settings from base.py, you do not need
# to import base above
INSTALLED_APPS = base.INSTALLED_APPS + (
    # 'django_nose',
    'debug_toolbar',
    'debug_panel',
    'django_extensions'
)

MIDDLEWARE_CLASSES = base.MIDDLEWARE_CLASSES + (
    'debug_panel.middleware.DebugPanelMiddleware',
)

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES_TEST = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(base.BASE_DIR, 'db.sqlite3'),
        'ATOMIC_REQUESTS': True,
    }
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'moneypot_dist',
        'USER': 'moneypot',
        'PASSWORD': os.getenv("PG_PASSWORD", ""),
        'HOST': '',
        'ATOMIC_REQUESTS': True
    }
}

# if 'test' in sys.argv:
#     DATABASES = DATABASES_TEST

# Recipients of traceback emails and other notifications.
ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)
MANAGERS = ADMINS

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# SECURITY WARNING: don't run with debug turned on in production!
# Debugging displays nice error messages, but leaks memory. Set this to False
# on all server instances and True only for development.
DEBUG = True

# Is this a development instance? Set this to True on development/master
# instances and False on stage/prod.
DEV = True

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY", "")

## Log settings

# Remove this configuration variable to use your custom logging configuration
LOGGING_CONFIG = None
LOGGING = {
    'version': 1,
    'loggers': {
        'moneypot': {
            'level': "DEBUG"
        }
    }
}

INTERNAL_IPS = ('127.0.0.1',)

LANGUAGE_CODE = 'uk'
# LANGUAGE_CODE = 'en'