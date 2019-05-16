from django import template

register = template.Library()


@register.filter
def decimal_to_hours(data):
    return str(data).replace(".", ":")
