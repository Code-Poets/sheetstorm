from django.core.validators import BaseValidator


class MaxDecimalValueValidator(BaseValidator):
    # class which need to stay because of dependency
    # with 0001_initial.py migration from employees model
    def compare(self, a, b):  # type: ignore
        # this method need to stay overwritten
        # because of check work_hours field during data migrations
        # from DecimalField into DurationField
        pass
