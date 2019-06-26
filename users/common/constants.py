import enum

from django.utils.translation import ugettext_lazy as _

DEFAULT_COUNTRY_CODE = "PL"

EMAIL_MAX_LENGTH = 255
FIRST_NAME_MAX_LENGTH = 30
LAST_NAME_MAX_LENGTH = 30
COUNTRY_MAX_LENGTH = 20
USER_TYPE_MAX_LENGTH = 20
PHONE_NUMBER_MAX_LENGTH = 15
PHONE_NUMBER_MIN_LENGTH = 9

PLACE_HOLDER_CAPTCHA = _("Enter the code above here")
CAPTCHA_SCALE_SIZE = 2


class ErrorCode(enum.Enum):
    CREATE_USER_EMAIL_MISSING = "header.user_email.missing"
    CREATE_USER_EMAIL_DOMAIN = "header.user_email.domain"
    CREATE_USER_EMAIL_SIGN_MISSING = "header.user_email_sign.missing"
    CREATE_USER_PASSWORD_MISSING = "header.user_password.missing"
