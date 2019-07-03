import datetime
import re
from typing import Optional

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible

from users.common.strings import ValidationErrorText


@deconstructible
class UserAgeValidator:
    MINIMAL_ACCETABLE_AGLE = 18
    MAXIMAL_ACCEPTABLE_AGE = 99

    def __init__(self, minimal_age: int, maximal_age: int) -> None:
        self.minimal_age = minimal_age
        self.maximal_age = maximal_age

    def __call__(self, users_birth_date: Optional[datetime.date]) -> Optional[datetime.date]:
        if users_birth_date is not None:
            age = relativedelta(datetime.datetime.now(), users_birth_date).years
            if not self.MINIMAL_ACCETABLE_AGLE <= age <= self.MAXIMAL_ACCEPTABLE_AGE:
                raise ValidationError(ValidationErrorText.VALIDATION_ERROR_AGE_NOT_ACCEPTED)
        return users_birth_date


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
