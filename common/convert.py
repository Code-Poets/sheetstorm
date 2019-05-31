from datetime import timedelta
from typing import Tuple
from typing import Union

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as RestValidationError


def timedelta_to_string(data: timedelta) -> str:
    days = data.days
    hours = data.seconds // 3600
    minutes = (data.seconds % 3600) // 60
    return "{:02d}:{:02d}".format((hours + (days * 24)) if days > 0 else hours, minutes)


def convert_string_work_hours_field_to_hour_and_minutes(
    data: str, exception: Union[RestValidationError, DjangoValidationError]
) -> Tuple[str, str]:
    # parameter `exception` is only workaround until we get rid of rest_framework views.
    # After this we will substitute it with django ValidationError
    if str(data).count(":") != 1:
        if not data.isdigit():
            raise exception
        else:
            hours = data
            minutes = "00"
    else:
        hours, minutes = str(data).split(":")
        if not hours.isdigit() or not minutes.isdigit():
            raise exception
    return (hours, minutes)
