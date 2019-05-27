import logging
import random
import string

from django.core.exceptions import ValidationError

from users.common import constants
from users.common.constants import ErrorCode
from users.common.strings import ValidationErrorText

logger = logging.getLogger(__name__)


def generate_random_string_from_letters_and_digits(length):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_random_phone_number(length):
    return "".join(random.choices(string.digits, k=length))


def custom_validate_email_function(email):
    logger.info(f"Custom validate email function with email: {email}")
    if email.count("@") == 1:
        if email.split("@")[0] in ["", " "]:
            logger.warning(f"Empty first part in email")
            raise ValidationError(
                message=ValidationErrorText.VALIDATION_ERROR_EMAIL_MALFORMED_FIRST_PART,
                code=ErrorCode.CREATE_USER_EMAIL_MISSING,
            )

        else:
            if email.split("@")[1] not in constants.VALID_EMAIL_DOMAIN_LIST:
                logger.warning(f"Invalid email domain: {email}")
                raise ValidationError(
                    message=ValidationErrorText.VALIDATION_ERROR_EMAIL_MESSAGE_DOMAIN,
                    code=ErrorCode.CREATE_USER_EMAIL_DOMAIN,
                )
    else:
        logger.warning(f"Invalid email: {email}. It should consist of name.surname@codepoets.it")
        raise ValidationError(
            message=ValidationErrorText.VALIDATION_ERROR_EMAIL_AT_SIGN_MESSAGE,
            code=ErrorCode.CREATE_USER_EMAIL_SIGN_MISSING,
        )
