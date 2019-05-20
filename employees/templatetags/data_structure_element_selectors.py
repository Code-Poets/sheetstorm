from typing import Any
from typing import Dict

from django import template

register = template.Library()


@register.filter
def get_key_value(dictionary: Dict[Any, Any], index: Any) -> Any:
    return dictionary.get(index, "")
