"""
Django settings for fondefVizServer project.

Generated by 'django-admin startproject' using Django 1.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
import fondefVizServer.keys.database as database
import fondefVizServer.keys.secret_key as secretKey
from elasticsearch import Elasticsearch

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = secretKey.SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [u'10.0.2.15', u'127.0.0.1', u'localhost', '200.9.100.91', u'172.17.74.243', u'172.17.57.156']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bowerapp',
    'profile',
    'velocity',
    'travel',
    'datamanager',
    'localinfo',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
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
            ],
        },
    },
]

WSGI_APPLICATION = 'fondefVizServer.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = database.DATABASES

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
ES_CLIENT = Elasticsearch("172.17.57.47:9200", http_auth=('elastic', 'changeme'))

# devel mode
# - allows manage.py runserver
# - allows development without messing up the official ES server.
if DEBUG:
    # this allows to serve static files when runing: python manage.py runserver
    # but is not safe and requires the STATIC_ROOT variable is not defined.
    del STATIC_ROOT
    STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static/'), )

    # Provide another ES client, which hooks to this machine and not the
    # official one. To use this connection, simply provide the 'using' param
    # when creating a new elasticsearch_dsl.Search object:
    #    client = settings.ES_CLIENT_DEVEL
    #    es_query = Search(using=client, index="my-index-pattern")
    ES_CLIENT_DEVEL = Elasticsearch([
        {'host': 'localhost', 'port': 9200},
    ])
