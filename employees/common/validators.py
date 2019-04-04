from django.core.validators import BaseValidator

from employees.common.strings import MAX_DECIMAL_VALUE_VALIDATOR_MESSAGE


class MaxDecimalValueValidator(BaseValidator):
    message = MAX_DECIMAL_VALUE_VALIDATOR_MESSAGE
    code = "max_decimal_value"

    def compare(self, a, b):
        return a > b

    def clean(self, x):
        return x % 1
