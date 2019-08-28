import re
from typing import Optional

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible

from users.common.strings import ValidationErrorText


@deconstructible
class UserAgeValidator:
    # TODO: Delete this class in next squash migrations
    pass


@deconstructible
class UserEmailValidation:
    def __call__(self, email: Optional[str]) -> Optional[str]:
        if email is not None and email.count("@") == 1:
            if email.split("@")[0] in ["", " "]:
                raise ValidationError(message=ValidationErrorText.VALIDATION_ERROR_EMAIL_MALFORMED_FIRST_PART)

            else:
                if email.split("@")[1] not in settings.VALID_EMAIL_DOMAIN_LIST:
                    raise ValidationError(message=ValidationErrorText.VALIDATION_ERROR_EMAIL_MESSAGE_DOMAIN)
        else:
            raise ValidationError(message=ValidationErrorText.VALIDATION_ERROR_EMAIL_AT_SIGN_MESSAGE)
        return email


@deconstructible
class UserNameValidatior:
    def __init__(self) -> None:
        self.regex = re.compile(
            "[\"'@_!#$%^&*()<>?/|}{~:;\]\[=+\\\]"  # noqa: W605  # pylint: disable=anomalous-backslash-in-string
        )

    def __call__(self, name: Optional[str]) -> Optional[str]:
        if isinstance(name, str):
            if self.regex.search(name):
                raise ValidationError(message=ValidationErrorText.VALIDATION_ERROR_SPECIAL_CHARACTERS_IN_NAME)
        return name
