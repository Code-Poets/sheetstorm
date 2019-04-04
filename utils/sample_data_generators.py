import math
from decimal import Decimal

# Both functions can't have correct typing because of bug in mypy: https://github.com/python/mypy/issues/6211


def generate_decimal_with_digits(digits, constant=math.e / 2):  # type: ignore
    assert isinstance(digits, int) and digits > 1
    assert 0 < constant < 10
    return round(Decimal((constant * 10 ** (digits - 2))), 1)


def generate_decimal_with_decimal_places(decimal_places, constant=math.e / 2):  # type: ignore
    assert isinstance(decimal_places, int) and decimal_places > 0
    assert 0 < constant < 10
    return round(Decimal(constant), decimal_places)
