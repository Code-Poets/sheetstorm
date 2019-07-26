import calendar
import re
from datetime import timedelta

from django import template
from django.utils.safestring import mark_safe

from common.convert import timedelta_to_string

register = template.Library()


@register.filter
def duration_field_to_string(data: timedelta) -> str:
    return timedelta_to_string(data)


@register.filter
def convert_to_month_name(month_number: str) -> str:
    return calendar.month_name[int(month_number)]


@register.filter
def annotate_no_follow_link_with_css_class(html: str, css_class: str) -> str:
    nofollow = 'rel="nofollow"'
    nofollow_length = len(nofollow)
    if nofollow not in html:
        return html
    class_parameter = f'class="{css_class}"'
    for pos in reversed([match.start() for match in re.finditer(nofollow, html)]):
        html = f"{html[:pos + nofollow_length]} {class_parameter}{html[pos + nofollow_length:]}"

    return mark_safe(html)
