import calendar
import re
from datetime import timedelta
from typing import List

from django import template
from django.db.models.functions import datetime

from common.convert import timedelta_to_string

register = template.Library()


@register.filter
def duration_field_to_string(data: timedelta) -> str:
    return timedelta_to_string(data)


@register.filter
def extract_year_and_month_from_url(url: str) -> List[str]:
    regex = re.compile(r"/(?P<year>[0-9]{4})/(?P<month>[0-9]{1,2})$")
    date = regex.search(url)

    if date is not None:
        year = date.group("year")
        month = date.group("month")
    else:
        now = datetime.datetime.now()
        year = now.year
        month = now.month

    return [year, month]


@register.filter
def convert_to_month_name(month_number: str) -> str:
    return calendar.month_name[int(month_number)]
