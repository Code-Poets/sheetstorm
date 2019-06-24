import calendar
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
    splitted_url = url.split("/")
    while "" in splitted_url:
        splitted_url.remove("")

    if splitted_url[-2].isdigit() and splitted_url[-1].isdigit():
        year = splitted_url[-2]
        month = splitted_url[-1]
    else:
        now = datetime.datetime.now()
        year = now.year
        month = now.month

    return [year, month]


@register.filter
def convert_to_month_name(month_number: str) -> str:
    return calendar.month_name[int(month_number)]
