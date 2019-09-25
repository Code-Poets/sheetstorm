from .base import *

ENVIRONMENT = 'production'

DEBUG = False

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

SITE_ID = 2

VALID_EMAIL_DOMAIN_LIST = ["codepoets.it"]

CSRF_COOKIE_SECURE = True

SESSION_COOKIE_SECURE = True
