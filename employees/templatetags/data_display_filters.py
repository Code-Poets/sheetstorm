from datetime import timedelta

from django import template

register = template.Library()


@register.filter
def duration_field_to_string(data: timedelta) -> str:
    return "{:02d}:{:02d}".format((data.seconds // 3600), (data.seconds % 3600) // 60)
