from decimal import Decimal
from enum import Enum


class ReportModelConstants(Enum):
    MAX_DESCRIPTION_LENGTH = 1024
    MAX_DIGITS = 4
    DECIMAL_PLACES = 2
    MAX_WORK_HOURS = Decimal("24.00")
    MIN_WORK_HOURS = Decimal("0.01")
    MAX_WORK_HOURS_DECIMAL_VALUE = Decimal("0.59")
    TASK_ACTIVITIES_MAX_LENGTH = 20
