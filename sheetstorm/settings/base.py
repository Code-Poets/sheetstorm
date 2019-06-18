"""
Django settings for sheetstorm project.

Generated by 'django-admin startproject' using Django 1.11.12.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# Secret key is used for generating hashes, such as authentication tokens and secured cookies.
# It should be located in your local_settings.py.
#SECRET_KEY = ''

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []  # type: ignore


# Application definition

INSTALLED_APPS = [
    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django_countries',
    'users',
    # 3rd party
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'bootstrap_datepicker_plus',
    'crispy_forms',
    'raven.contrib.django.raven_compat',
    # SheetStorm
    'managers.apps.ManagersConfig',
    'employees.apps.EmployeesConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'raven.contrib.django.raven_compat.middleware.Sentry404CatchMiddleware',
]

ROOT_URLCONF = 'sheetstorm.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
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

WSGI_APPLICATION = 'sheetstorm.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE':           'django.db.backends.postgresql',
        'NAME':             'sheetstorm',
        'ATOMIC_REQUESTS':  True,
        # 'USER':     'postgres',
        # 'PASSWORD': '',
        # 'HOST':     '',
        # 'PORT':     '',
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


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


LOGGING = {
    'version':                  1,
    'disable_existing_loggers': False,
    'formatters':               {
        'console': {
            'format':  '%(asctime)s %(levelname)-8s | %(message)s',
            'datefmt': '%H:%M:%S',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        }
    },
    'handlers': {
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        },
        'mail_admins': {
            'level':   'ERROR',
            'filters': ['require_debug_false'],
            'class':   'django.utils.log.AdminEmailHandler',
        },
        'console': {
            'level':     'INFO',
            'class':     'logging.StreamHandler',
            'formatter': 'console',
        },
    },
    'loggers': {
        # NOTE: There are a few important caveats you need to consider when tweaking logging:
        # - If a message is logged to logger 'a.b' and propagates to logger 'a', only the level of logger
        #   'a.b' counts. Level of logger 'a' is ignored. Not kidding. See the diagram:
        #   https://docs.python.org/3/howto/logging.html#logging-flow
        # - level of logger 'a.b' determines not only what it handles but also what it propagates to parent.
        # - If a logger has no level, it inherits level from parent. Root logger (the one called '') has level WARNING by default.

        # RULES: Try to stick to the following conventions:
        # - Don't set level of a logger unless you explicitly want to prevent some messages from being handled or propagated.
        # - In most cases it's better to leave level at DEBUG here and set level in handler instead.
        # - Set level explicitly if you don't propagate. Such a logger should not be dependent on parent's level.
        # - Don't propagate to the root logger if the output is very verbose. Use a separate handler/file instead.
        # - Log at INFO level should be concise and contain only important stuff. Enough to understand what
        #   is happening but not necessarily why. DEBUG level can be more spammy.

        '': {
            # Logging to the console. The application is primarily going to run in foreground inside Docker container
            # and we want Docker to capture all that output. You can add an extra file handler in your local_settings.py
            # if you think you really need it. Do keep in mind though that log files need to be rotated or they'll eat
            # a lot of disk space.
            'handlers':  ['console'],
            # NOTE: Changing level of this logger will change levels of loggers from plugins
            # because they often don't have a level set explicitly and inherit this one instead.
            'level':     'DEBUG',
            'propagate': False,
        },
        'py.warnings': {
            # Prevent Python from printing its warnings to the console. Our top-level logger already handles and prints them.
            # I'm not entirely sure why this works but I think that the default py.warnings has a custom console handler
            # attached and by defining it here we're overwriting it and disabling the handler.
            'level':     'DEBUG',
            'propagate': True,
        },
        'django': {
            # Redefine django logger without handlers. Otherwise errors propagated from django.request
            # get logged to the console twice.
            'handlers':  [],
            'level':     'DEBUG',
            'propagate': True,
        },
        'django.db': {
            # Filter out DEBUG messages. There are too many of them. Django logs all DB queries at this level.
            'level':     'INFO',
            'propagate': True,
        },
        'django.request': {
            # Level is DEBUG because we're leaving filtering up to the handler.
            'handlers':  ['sentry'],
            'level':     'DEBUG',
            'propagate': True,
        },
        'sheetstorm.crash': {
            # Level is DEBUG because we're leaving filtering up to the handler.
            'handlers':  ['sentry'],
            'level':     'DEBUG',
            'propagate': True,
        },
    },
}


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

AUTH_USER_MODEL = 'users.CustomUser'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'login'


ACCOUNT_USERNAME_REQUIRED = False

ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_AUTHENTICATION_METHOD = 'email'

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_USER_EMAIL_FIELD = 'email'
ACCOUNT_LOGOUT_ON_GET = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

SITE_ID = 1

FIXTURE_DIRS = [
    'users/fixtures/',
    'managers/fixtures/',
    'employees/fixtures/',
]

COUNTRIES_FIRST = [
    'PL',
    'GB',
    'DE',
    'FR',
    'US',
]

CRISPY_TEMPLATE_PACK = 'bootstrap4'
