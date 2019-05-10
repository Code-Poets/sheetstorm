import logging
import random
import string

from rest_framework import serializers

from users.common import constants
from users.common.constants import ErrorCode
from users.common.exceptions import CustomValidationError
from users.common.strings import CustomValidationErrorText

logger = logging.getLogger(__name__)


def generate_random_string_from_letters_and_digits(length):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_random_phone_number(length):
    return "".join(random.choices(string.digits, k=length))


def raise_serializer_exception(error_message):
    logger.warning(f"Serializer raised exception with message: {error_message}")
    raise serializers.ValidationError(error_message)


def raise_custom_validation_exception(error_message, error_code):
    logger.warning(f"Custom valid exception with message: {error_message} and error code: {error_code}")
    raise CustomValidationError(error_message, error_code)


def prepare_proper_exception(call_instance, error_message, error_code):
    if "serializers" in str(type(call_instance)):
        logger.debug(
            f"Serializer: {call_instance} caught exception with message: {error_message} and error_code: {error_code}"
        )
        raise_serializer_exception(error_message)
    else:
        raise_custom_validation_exception(error_message, error_code)


def custom_validate_email_function(call_instance, email):
    logger.info(f"Custom validate email function with email: {email} sent from: {type(call_instance)}")
    if email.count("@") == 1:
        if email.split("@")[0] in ["", " "]:
            logger.debug(f"Empty first part in email")
            prepare_proper_exception(
                call_instance,
                CustomValidationErrorText.VALIDATION_ERROR_EMAIL_MALFORMED_FIRST_PART,
                ErrorCode.CREATE_USER_EMAIL_MISSING,
            )

        else:
            if email.split("@")[1] not in constants.VALID_EMAIL_DOMAIN_LIST:
                logger.debug(f"Invalid email domain: {email}")
                prepare_proper_exception(
                    call_instance,
                    CustomValidationErrorText.VALIDATION_ERROR_EMAIL_MESSAGE_DOMAIN,
                    ErrorCode.CREATE_USER_EMAIL_DOMAIN,
                )
    else:
        logger.debug(f"Invalid email: {email}. It should consist of name.surname@codepoets.it")
        prepare_proper_exception(
            call_instance,
            CustomValidationErrorText.VALIDATION_ERROR_EMAIL_AT_SIGN_MESSAGE,
            ErrorCode.CREATE_USER_EMAIL_SIGN_MISSING,
        )
