from django import template

register = template.Library()


@register.filter("startswith")
def startswith(text: str, starts: str) -> bool:
    if isinstance(text, str):
        if starts not in ["", " "]:
            return text.startswith(starts)
    return False
