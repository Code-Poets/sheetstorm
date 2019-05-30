from datetime import timedelta
from enum import Enum


class ReportModelConstants(Enum):
    MAX_DESCRIPTION_LENGTH = 4096
    MAX_WORK_HOURS = timedelta(hours=24)
    MIN_WORK_HOURS = timedelta(minutes=1)


class TaskActivityTypeConstans(Enum):
    TASK_ACTIVITIES_MAX_LENGTH = 30


class ExcelGeneratorSettingsConstants(Enum):
    TOTAL = "Total"
    HEADERS_ROW = 1
    FIRST_ROW_FOR_DATA = 2
    HEADERS_FOR_SINGLE_USER = ["Date", "Project", "Task activity", "Hours", "Description"]
    COLUMNS_WIDTH_FOR_SINGLE_USER = [12, 20, 30, 6, 100]
    COLUMNS_WIDTH_FOR_PROJECT = [12, 30, 6, 100]
    HEADERS_FOR_USER_IN_PROJECT = ["Date", "Task activity", "Hours", "Description"]
    HOURS_COLUMN_FOR_REPORTS_IN_PROJECT = 3
    TOTAL_COLUMN = 1
    DESCRIPTION_COLUMN_FOR_SINGLE_USER = 5
    DESCRIPTION_COLUMN_FOR_REPORTS_IN_PROJECT = 4
    HOURS_COLUMN_FOR_SINGLE_USER = 4
    VERCTICAL_TOP = "top"
    CENTER_ALINGMENT = "center"
    FONT = "Calibri"
    HOURS_FORMAT = "h:mm"
    TIMEVALUE_FORMULA = '=timevalue("{}")'
    TOTAL_HOURS_FORMAT = "[h]:mm"
    TOTAL_HOURS_FORMULA_FOR_SINGLE_USER = "=SUM(D1:D{})"
    TOTAL_HOURS_FORMULA_REPORTS_IN_PROJECT = "=SUM(C1:C{})"
    CONTENT_TYPE_FORMAT = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    EXPORTED_FILE_NAME = 'attachment; filename="{}_{}-reports.xlsx"'
    BORDER = "double"
