from .development import *

ALLOWED_HOSTS = [
    '172.30.2.3',
]

DATABASES['default']['USER']     = 'postgres'
DATABASES['default']['PASSWORD'] = ''
DATABASES['default']['HOST']     = ''
DATABASES['default']['PORT']     = ''
