# -*- encoding: utf-8 -*-
from __future__ import print_function, division, unicode_literals, absolute_import

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__) + "../../../")

import sys
from django.db.backends.signals import connection_created
from django.db.utils import ProgrammingError
from django.db import connection

try:
    reload(sys)  # Reload does the trick for python 2.7
    sys.setdefaultencoding('UTF8')
except NameError as e:
    pass     # No reload - no issues. We are running python 3 ...


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

SITE_ID = 1

# Application definition

INSTALLED_APPS = (
    # core batteries
    'autocomplete_light',
    'grappelli',
    'grappelli_filters',
    'filebrowser',
    # django stuff
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.flatpages',
    # batteries
    'corsheaders',
    'mptt',
    'django_mptt_admin',
    'djorm_pgtrgm',
    'downtime',
    # 'guardian',
    'daterange_filter',
    'rest_framework',
    'rest_framework.authtoken',
    'gitrevision',
    'sorl.thumbnail',
    # project apps
    'userprofile',
    'base',
)

MIDDLEWARE_CLASSES = (
    'downtime.middleware.DowntimeMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'gitrevision.middleware.GitRevision',
    'moneypot.middleware.ExceptionMiddleware',
    'moneypot.middleware.StaticRevision',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(PROJECT_ROOT, 'templates'),
        ],
        'OPTIONS': {
            'loaders': (
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader'
            ),
            'debug': DEBUG,
            'context_processors': (
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.core.context_processors.request",
                "django.contrib.messages.context_processors.messages",
                "gitrevision.context_processors.gitrevision",
            )
        }
    },
]

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',  # default
    # 'guardian.backends.ObjectPermissionBackend',
)

CORS_ORIGIN_ALLOW_ALL = True

ANONYMOUS_USER_ID = -1

ROOT_URLCONF = 'moneypot.urls'

WSGI_APPLICATION = 'moneypot.wsgi.application'

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

# LANGUAGE_CODE = 'uk'
LANGUAGE_CODE = 'en'

TIME_ZONE = 'Europe/Kiev'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = (
    os.path.join(PROJECT_ROOT, 'locale'),
)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')

VERSIONS_BASEDIR = "_versions"

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 20
}

VERSION = "1.0.4"
RELEASE_NOTES_URL = "/p/release-1.0.4/"
GRAPPELLI_ADMIN_TITLE = "Склад. версія %s" % VERSION

THUMBNAIL_DUMMY = True
PLACEHOLDER_IMAGE_PATH = "%s/%s" % (STATIC_ROOT, "base/img/empty.gif")

APP_FILTERS = {
    'CAT_ORDERS_ID': 85,
    'CAT_CONTRACTS_ID': 74,
    'PLACE_STORAGE_ID': 6,
    'PLACE_WORKERS_ID': 3,
    'PLACE_ADDRESS_ID': 40,
    'PLACE_USED_ID': 59,
    'PLACE_TRANSMUTATOR_ID': 502,
    'PLACE_UNSORTED_ID': 9882,
    'PLACE_VOID': 152,
    'PLACE_OLD_STORAGE': 1,
    'PAYER_OLD_STORAGE': 1,
    'GROUP_WORKERS_ID': 4
}


def db_connection_init(sender, **kwargs):
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT set_limit(0.1);")
    except ProgrammingError:
        print("Trigram search not available!")

connection_created.connect(db_connection_init)