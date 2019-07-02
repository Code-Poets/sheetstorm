from .base import *

ENVIRONMENT = 'development'

DEBUG = True

SECRET_KEY = '12345abcdef'  # Can be any string

DATABASES['default']['USER']     = 'postgres'
DATABASES['default']['PASSWORD'] = ''
DATABASES['default']['HOST']     = ''
DATABASES['default']['PORT']     = ''

CAPTCHA_TEST_MODE = True

VALID_EMAIL_DOMAIN_LIST = ["codepoets.it"]
