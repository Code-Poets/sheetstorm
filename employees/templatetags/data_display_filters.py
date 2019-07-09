import calendar
from datetime import timedelta

from django import template

from common.convert import timedelta_to_string

register = template.Library()


@register.filter
def duration_field_to_string(data: timedelta) -> str:
    return timedelta_to_string(data)


@register.filter
def convert_to_month_name(month_number: str) -> str:
    return calendar.month_name[int(month_number)]
