from datetime import timedelta
from enum import Enum


class ReportModelConstants(Enum):
    MAX_DESCRIPTION_LENGTH = 4096
    MAX_WORK_HOURS = timedelta(hours=24)
    MIN_WORK_HOURS = timedelta(minutes=1)


class TaskActivityTypeConstans(Enum):
    TASK_ACTIVITIES_MAX_LENGTH = 30
