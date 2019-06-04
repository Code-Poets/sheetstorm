from datetime import timedelta
from enum import Enum

MONTH_NAVIGATION_FORM_MAX_MONTH_VALUE = 12
MONTH_NAVIGATION_FORM_MIN_MONTH_VALUE = 5
MONTH_NAVIGATION_FORM_MAX_YEAR_VALUE = 2099
MONTH_NAVIGATION_FORM_MIN_YEAR_VALUE = 2019


class ReportModelConstants(Enum):
    MAX_DESCRIPTION_LENGTH = 4096
    MAX_WORK_HOURS = timedelta(hours=24)
    MIN_WORK_HOURS = timedelta(minutes=1)


class TaskActivityTypeConstans(Enum):
    TASK_ACTIVITIES_MAX_LENGTH = 30


class ExcelGeneratorSettingsConstants(Enum):
    TOTAL = "Total"
    HEADERS_ROW = 1
    TOTAL_COLUMN = 1
    FIRST_ROW_FOR_DATA = 2

    HEADERS_FOR_SINGLE_USER = ["Date", "Daily hours", "Project", "Task activity", "Hours", "Description"]
    COLUMNS_WIDTH_FOR_SINGLE_USER = [12, 12, 20, 30, 6, 100]
    DAILY_HOURS_COLUMN_FOR_SINGLE_USER = 2
    HOURS_COLUMN_FOR_SINGLE_USER = 5
    DESCRIPTION_COLUMN_FOR_SINGLE_USER = 6

    HEADERS_FOR_USER_IN_PROJECT = ["Date", "Daily hours", "Task activity", "Hours", "Description"]
    COLUMNS_WIDTH_FOR_PROJECT = [12, 12, 30, 6, 100]
    DAILY_HOURS_COLUMN_FOR_REPORTS_IN_PROJECT = 2
    HOURS_COLUMN_FOR_REPORTS_IN_PROJECT = 4
    DESCRIPTION_COLUMN_FOR_REPORTS_IN_PROJECT = 5

    VERCTICAL_TOP = "top"
    CENTER_ALINGMENT = "center"
    FONT = "Calibri"
    HOURS_FORMAT = "h:mm"
    TIMEVALUE_FORMULA = '=timevalue("{}")'
    TOTAL_HOURS_FORMAT = "[h]:mm"
    TOTAL_HOURS_FORMULA_FOR_SINGLE_USER = "=SUM(E1:D{})"
    TOTAL_HOURS_FORMULA_REPORTS_IN_PROJECT = "=SUM(D1:C{})"
    CONTENT_TYPE_FORMAT = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    EXPORTED_FILE_NAME = 'attachment; filename="{}_{}-reports.xlsx"'
    BORDER = "double"
