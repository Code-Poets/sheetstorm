import datetime
from django.utils.deconstruct import deconstructible
from typing import Optional

from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError

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
