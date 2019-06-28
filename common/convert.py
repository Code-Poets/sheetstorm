from datetime import timedelta
from typing import Optional
from typing import Tuple

from django.core.exceptions import ValidationError

from employees.common.strings import ReportValidationStrings


def timedelta_to_string(data: Optional[timedelta]) -> str:
    if data is None:
        return ""
    days = data.days
    hours = data.seconds // 3600
    minutes = (data.seconds % 3600) // 60
    return "{:02d}:{:02d}".format((hours + (days * 24)) if days > 0 else hours, minutes)


def convert_string_work_hours_field_to_hour_and_minutes(data: str) -> Tuple[str, str]:
    if str(data).count(":") != 1:
        if not data.isdigit():
            raise ValidationError(message=ReportValidationStrings.WORK_HOURS_WRONG_FORMAT.value)
        else:
            hours = data
            minutes = "00"
    else:
        hours, minutes = str(data).split(":")
        if not hours.isdigit() or not minutes.isdigit():
            raise ValidationError(message=ReportValidationStrings.WORK_HOURS_WRONG_FORMAT.value)
    return (hours, minutes)
