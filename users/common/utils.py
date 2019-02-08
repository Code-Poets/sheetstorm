from rest_framework import serializers

from users.common import constants
from users.common.constants import ErrorCode
from users.common.exceptions import CustomValidationError
from users.common.strings import CustomValidationErrorText


def raise_serializer_exception(error_message):
    raise serializers.ValidationError(error_message)


def raise_custom_validation_exception(error_message, error_code):
    raise CustomValidationError(
        error_message,
        error_code,
    )


def prepare_proper_exception(call_instance, error_message, error_code):
    if 'serializers' in str(type(call_instance)):
        raise_serializer_exception(error_message)
    else:
        raise_custom_validation_exception(error_message, error_code)


def custom_validate_email_function(call_instance, email):
    if email.count('@') == 1:
        if email.split('@')[0] in ['', ' ']:
            prepare_proper_exception(
                call_instance,
                CustomValidationErrorText.VALIDATION_ERROR_EMAIL_MALFORMED_FIRST_PART,
                ErrorCode.CREATE_USER_EMAIL_MISSING,
            )

        else:
            if email.split('@')[1] not in constants.VALID_EMAIL_DOMAIN_LIST:
                prepare_proper_exception(
                    call_instance,
                    CustomValidationErrorText.VALIDATION_ERROR_EMAIL_MESSAGE_DOMAIN,
                    ErrorCode.CREATE_USER_EMAIL_DOMAIN,
                )
    else:
        prepare_proper_exception(
            call_instance,
            CustomValidationErrorText.VALIDATION_ERROR_EMAIL_AT_SIGN_MESSAGE,
            ErrorCode.CREATE_USER_EMAIL_SIGN_MISSING,
        )
