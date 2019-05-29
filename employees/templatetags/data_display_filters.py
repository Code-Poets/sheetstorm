from datetime import timedelta

from django import template

from common.convert import timedelta_to_string

register = template.Library()


@register.filter
def duration_field_to_string(data: timedelta) -> str:
    return timedelta_to_string(data)
