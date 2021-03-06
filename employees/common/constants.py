from datetime import timedelta
from enum import Enum
from typing import NamedTuple

from openpyxl.styles import Side


class MonthNavigationConstants(Enum):
    MAX_MONTH_VALUE = 12
    MIN_MONTH_VALUE = 5
    MAX_YEAR_VALUE = 2099
    MIN_YEAR_VALUE = 2019


class ReportModelConstants(Enum):
    MAX_DESCRIPTION_LENGTH = 4096
    MAX_WORK_HOURS = timedelta(hours=24)
    MIN_WORK_HOURS = timedelta(minutes=15)


class TaskActivityTypeConstans(Enum):
    TASK_ACTIVITIES_MAX_LENGTH = 30


class ColumnSettings(NamedTuple):
    position: int
    width: int


class ExcelGeneratorSettingsConstants(Enum):
    TOTAL = "Total"
    EMPLOYEE_NAME_ROW = 1
    EMPLOYEE_NAME_START_COLUMN = 1
    EMPLOYEE_NAME_END_COLUMN = 3
    EMPLOYEE_NAME = "EMPLOYEE: {}"
    HEADERS_ROW = 2
    TOTAL_COLUMN = 1
    FIRST_ROW_FOR_DATA = 3
    DEFAULT_ROW_HEIGHT = 15
    MAX_DESCRIPTION_WIDTH = 100

    DATE_HEADER_STR = "Date"
    PROJECT_HEADER_STR = "Project"
    TASK_ACTIVITY_HEADER_STR = "Task activity"
    HOURS_HEADER_STR = "Hours"
    DESCRIPTION_HEADER_STR = "Description"

    HEADERS_TO_COLUMNS_SETTINGS_FOR_SINGLE_USER = {
        DATE_HEADER_STR: ColumnSettings(position=1, width=12),
        PROJECT_HEADER_STR: ColumnSettings(position=2, width=20),
        TASK_ACTIVITY_HEADER_STR: ColumnSettings(position=3, width=30),
        HOURS_HEADER_STR: ColumnSettings(position=4, width=6),
        DESCRIPTION_HEADER_STR: ColumnSettings(position=5, width=100),
    }

    HEADERS_TO_COLUMNS_SETTINGS_FOR_USER_IN_PROJECT = {
        DATE_HEADER_STR: ColumnSettings(position=1, width=12),
        TASK_ACTIVITY_HEADER_STR: ColumnSettings(position=2, width=30),
        HOURS_HEADER_STR: ColumnSettings(position=3, width=6),
        DESCRIPTION_HEADER_STR: ColumnSettings(position=4, width=100),
    }

    VERCTICAL_TOP = "top"
    CENTER_ALINGMENT = "center"
    FONT = "Calibri"
    HOURS_FORMAT = "h:mm"
    TOTAL_HOURS_FORMAT = "[h]:mm"
    XLSX_CONTENT_TYPE_FORMAT = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    XLSX_EXPORTED_FILE_NAME = 'attachment; filename="{}_{}-reports.xlsx"'
    CSV_CONTENT_TYPE_FORMAT = "application/csv"
    CSV_EXPORTED_FILE_NAME = 'attachment; filename="{}_{}-reports.csv"'
    BORDER = "double"
    BORDER_STYLE = Side(style=f"{'double'}")
