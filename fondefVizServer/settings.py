"""
Django settings for fondefVizServer project.

Generated by 'django-admin startproject' using Django 1.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""
import os

from ddtrace import patch
from decouple import config, Csv
from elasticsearch import Elasticsearch

patch(elasticsearch=True)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

INTERNAL_IPS = config('INTERNAL_IPS', cast=Csv())
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_crontab',
    'django_js_reverse',
    'django_rq',
    'ddtrace.contrib.django',
    'bowerapp',
    'esapi',
    'datamanager',
    'localinfo',
    'profile',
    'shape',
    'trip',
    'speed',
    'globalstat',
    'webuser',
    'debug_toolbar',
    'debug_panel',
    'logapp',
    'awsbackup',
    'paymentfactor',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'logapp.middleware.UserLogMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_panel.middleware.DebugPanelMiddleware'
]

ROOT_URLCONF = 'fondefVizServer.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'datamanager.context_processors.export_job'
            ],
        },
    },
]

WSGI_APPLICATION = 'fondefVizServer.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASS'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT')
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "rq_console": {
            "format": "%(asctime)s %(message)s",
            "datefmt": "%H:%M:%S",
        },
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(asctime)s %(message)s'
        }
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        }
    },
    "handlers": {
        "rq_console": {
            "level": "DEBUG",
            "class": "rq.utils.ColorizingStreamHandler",
            "formatter": "rq_console",
            "exclude": ["%(asctime)s"],
        },
        'file': {
            'level': 'DEBUG',
            'filters': ['require_debug_false'],
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(os.path.dirname(__file__), 'logs', 'file.log'),
            'maxBytes': 1024 * 1024 * 100,
            'backupCount': 10,
            'formatter': 'simple',
        },
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.template': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        "rq.worker": {
            "handlers": ["rq_console"],
            "level": "DEBUG"
        },
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'es-CL'

TIME_ZONE = 'Chile/Continental'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Elastic-Search settings
ES_CLIENT = Elasticsearch("{0}:{1}".format(config('ELASTICSEARCH_HOST'), config('ELASTICSEARCH_PORT')), timeout=600)

# Django js reverse settings
JS_REVERSE_EXCLUDE_NAMESPACES = []
JS_REVERSE_SCRIPT_PREFIX = config('URL_PREFIX')
JS_REVERSE_OUTPUT_PATH = os.path.join(BASE_DIR, os.path.join('bowerapp', os.path.join('static', 'js')))

# User url
LOGIN_URL = '{0}/user/login/'.format(JS_REVERSE_SCRIPT_PREFIX)
LOGIN_REDIRECT_URL = '{0}/'.format(JS_REVERSE_SCRIPT_PREFIX)

# user name to see all operator data
GLOBAL_PERMISSION_GROUP_NAME = 'Transantiago'

# django-rq task queueing
# reference: https://github.com/ui/django-rq
REDIS_CONF = {
    'HOST': config('REDIS_HOST'),
    'PORT': config('REDIS_PORT'),
    'DB': config('REDIS_DB'),
    'DEFAULT_TIMEOUT': 60 * 60 * 24,
}

RQ_QUEUES = {
    'data_uploader': REDIS_CONF,
    'data_exporter': REDIS_CONF,
    'count_lines': REDIS_CONF
}

RQ = {
    'DEFAULT_RESULT_TTL': 60 * 60 * 24
}

# custom handler to failed jobs
RQ_EXCEPTION_HANDLERS = ['rqworkers.tasks.upload_exception_handler', 'rqworkers.tasks.export_exception_handler']

# path to download files
DOWNLOAD_PATH = config('DOWNLOAD_PATH')

# email configuration
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)

EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')

SERVER_EMAIL = config('SERVER_EMAIL')

# crontab
CRONJOBS = [
    ('0 0 * * *', 'datamanager.cron.delete_old_file_job'),  # at 00:00 every day
    ('0 2 * * *', 'django.core.management.call_command',
     ['refreshusersession', '2018-01-01', '2030-01-01', '--delete-previous'], {})
]

# secure proxy SSL header and secure cookies
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# session expire at browser close
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# wsgi scheme
os.environ['wsgi.url_scheme'] = 'https'

DATADOG_TRACE = {
    'DEFAULT_SERVICE': config('DATADOG_SERVICE_NAME'),
    'DEFAULT_DATABASE_PREFIX': config('DATADOG_DB_PREFIX'),
    'DEFAULT_CACHE_SERVICE ': config('DATADOG_CACHE_SERVICE_NAME'),
    'TAGS': {'env': config('DATADOG_ENV')}
}
