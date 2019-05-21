from decimal import Decimal

from django import template

register = template.Library()


@register.filter
def decimal_to_hours(data: Decimal) -> str:
    return str(data).replace(".", ":")
