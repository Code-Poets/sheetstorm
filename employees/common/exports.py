from typing import List

from bs4 import BeautifulSoup
from openpyxl import Workbook
from openpyxl.cell import Cell
from openpyxl.styles import Alignment
from openpyxl.styles import Border
from openpyxl.styles import Font
from openpyxl.styles import Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

from employees.common.constants import ExcelGeneratorSettingsConstants
from employees.models import Report
from managers.models import Project
from users.models import CustomUser


def set_format_styles_for_main_cells(cell: Cell, is_header: bool):
    cell.font = Font(name=ExcelGeneratorSettingsConstants.FONT.value, bold=True)
    cell.alignment = Alignment(horizontal=ExcelGeneratorSettingsConstants.CENTER_ALINGMENT.value)
    border_style = Side(style=ExcelGeneratorSettingsConstants.BORDER.value)
    cell.border = (
        Border(bottom=border_style, top=border_style, right=border_style, left=border_style)
        if is_header
        else Border(top=border_style)
    )


def set_columns_width(worksheet: Worksheet, col_num: int, width_settings: list):
    column_letter = get_column_letter(col_num)
    column_dimensions = worksheet.column_dimensions[column_letter]
    column_dimensions.width = width_settings[col_num - 1]


def set_employee_name_is_worksheet(worksheet: Worksheet, employee_name: str):
    worksheet.merge_cells(
        start_row=ExcelGeneratorSettingsConstants.EMPLOYEE_NAME_ROW.value,
        end_row=ExcelGeneratorSettingsConstants.EMPLOYEE_NAME_ROW.value,
        start_column=ExcelGeneratorSettingsConstants.EMPLOYEE_NAME_START_COLUMN.value,
        end_column=ExcelGeneratorSettingsConstants.EMPLOYEE_NAME_END_COLUMN.value,
    )
    cell = worksheet.cell(
        row=ExcelGeneratorSettingsConstants.EMPLOYEE_NAME_ROW.value,
        column=ExcelGeneratorSettingsConstants.EMPLOYEE_NAME_START_COLUMN.value,
    )
    cell.value = ExcelGeneratorSettingsConstants.EMPLOYEE_NAME.value.format(employee_name)


def fill_headers(worksheet: Worksheet, headers: list, width_settings: list, employee_name: str):
    set_employee_name_is_worksheet(worksheet, employee_name)
    for col_num, column_title in enumerate(headers, 1):
        cell = worksheet.cell(row=ExcelGeneratorSettingsConstants.HEADERS_ROW.value, column=col_num)
        cell.value = column_title
        set_format_styles_for_main_cells(cell, is_header=True)
        set_columns_width(worksheet, col_num, width_settings)


def set_and_fill_description_cell(cell: Cell, cell_value: str):
    wrapped_alignment = Alignment(vertical=ExcelGeneratorSettingsConstants.VERCTICAL_TOP.value, wrap_text=True)
    cell.alignment = wrapped_alignment
    cell.value = cell_value


def set_and_fill_hours_cell(cell: Cell, cell_value: str):
    if cell_value is not None:
        cell.value = ExcelGeneratorSettingsConstants.TIMEVALUE_FORMULA.value.format(cell_value)
    else:
        cell.value = cell_value
    cell.number_format = ExcelGeneratorSettingsConstants.HOURS_FORMAT.value


def fill_current_report_data(storage_data: dict):
    for col_num, cell_value in enumerate(storage_data["data"], 1):
        cell = storage_data["worksheet"].cell(row=storage_data["current_row"], column=col_num)
        if col_num == storage_data["description_column"]:
            set_and_fill_description_cell(cell, cell_value)
        elif col_num == storage_data["hours_column"]:
            set_and_fill_hours_cell(cell, cell_value)
        elif col_num == storage_data["daily_hours_column"]:
            set_and_fill_hours_cell(cell, cell_value)
        else:
            cell.value = cell_value


def summarizing_reports(worksheet: Worksheet, last_row: int, hours_column: int, formula: str):
    total_cell = worksheet.cell(row=last_row, column=ExcelGeneratorSettingsConstants.TOTAL_COLUMN.value)
    total_cell.value = ExcelGeneratorSettingsConstants.TOTAL.value
    for column_number in range(1, worksheet.max_column + 1):
        set_format_styles_for_main_cells(worksheet.cell(row=last_row, column=column_number), is_header=False)

    total_hours_cell = worksheet.cell(row=last_row, column=hours_column)
    total_hours_cell.value = formula.format(last_row - 1)
    total_hours_cell.number_format = ExcelGeneratorSettingsConstants.TOTAL_HOURS_FORMAT.value
    set_format_styles_for_main_cells(total_hours_cell, is_header=False)


def get_employee_name(author: CustomUser) -> str:
    if author.last_name is not None and author.first_name is not None:
        return f"{author.first_name} {author.last_name}"
    else:
        return f"{author.email}"


def set_active_worksheet_name(workbook: Workbook, author: CustomUser) -> Worksheet:
    worksheet = workbook.active
    worksheet.title = get_employee_name(author)
    return worksheet


def get_report_date_and_daily_hours(reports_date: List[str], date: str, reports: Report):
    # returns report_date and daily_hours
    # if this is first occurrence of day
    # other way returns None

    def set_report_date_and_daily_hours(date: str, reports: Report, reports_date: List[str]):
        # set daily_hours from query method which gives summary of daily hours
        daily_hours = reports.get_report_work_hours_sum_for_date(date)
        reports_date.append(date)
        return (date, daily_hours, reports_date)

    daily_hours = None
    report_date = reports_date[-1] if len(reports_date) > 0 else None
    if report_date is not None:
        if report_date == date:
            report_date = None
        else:
            (report_date, daily_hours, reports_date) = set_report_date_and_daily_hours(date, reports, reports_date)
    else:
        (report_date, daily_hours, reports_date) = set_report_date_and_daily_hours(date, reports, reports_date)
    return (reports_date, report_date, daily_hours)


def generate_xlsx_for_single_user(author: CustomUser) -> Workbook:
    reports = author.get_reports_created()
    workbook = Workbook()
    worksheet = set_active_worksheet_name(workbook, author)
    employee_name = get_employee_name(author)
    fill_headers(
        worksheet,
        ExcelGeneratorSettingsConstants.HEADERS_FOR_SINGLE_USER.value,
        ExcelGeneratorSettingsConstants.COLUMNS_WIDTH_FOR_SINGLE_USER.value,
        employee_name,
    )
    current_row = ExcelGeneratorSettingsConstants.FIRST_ROW_FOR_DATA.value

    reports_date = []
    for report in reports:
        (reports_date, report_date, daily_hours) = get_report_date_and_daily_hours(reports_date, report.date, reports)
        report_data = {
            "data": [
                report_date,
                daily_hours,
                report.project.name,
                report.task_activities.name,
                report.work_hours_str,
                convert_markdown_html_to_text(report.markdown_description),
            ],
            "worksheet": worksheet,
            "current_row": current_row,
            "description_column": ExcelGeneratorSettingsConstants.DESCRIPTION_COLUMN_FOR_SINGLE_USER.value,
            "hours_column": ExcelGeneratorSettingsConstants.HOURS_COLUMN_FOR_SINGLE_USER.value,
            "daily_hours_column": ExcelGeneratorSettingsConstants.DAILY_HOURS_COLUMN_FOR_REPORTS_IN_PROJECT.value,
        }
        fill_current_report_data(report_data)
        current_row += 1

    summarizing_reports(
        worksheet,
        current_row,
        ExcelGeneratorSettingsConstants.HOURS_COLUMN_FOR_SINGLE_USER.value,
        ExcelGeneratorSettingsConstants.TOTAL_HOURS_FORMULA_FOR_SINGLE_USER.value,
    )
    return workbook


def generate_xlsx_for_project(project: Project) -> Workbook:
    authors = project.members.order_by("-last_name")
    workbook = Workbook()
    for author in authors:
        worksheet = set_active_worksheet_name(workbook, author)
        reports = project.report_set.filter(author=author.pk).order_by("-date")
        employee_name = get_employee_name(author)
        fill_headers(
            worksheet,
            ExcelGeneratorSettingsConstants.HEADERS_FOR_USER_IN_PROJECT.value,
            ExcelGeneratorSettingsConstants.COLUMNS_WIDTH_FOR_PROJECT.value,
            employee_name,
        )

        current_row = ExcelGeneratorSettingsConstants.FIRST_ROW_FOR_DATA.value
        reports_date = []
        for report in reports:
            (reports_date, report_date, daily_hours) = get_report_date_and_daily_hours(
                reports_date, report.date, reports
            )
            storage_data = {
                "data": [
                    report_date,
                    daily_hours,
                    report.task_activities.name,
                    report.work_hours_str,
                    convert_markdown_html_to_text(report.markdown_description),
                ],
                "worksheet": worksheet,
                "current_row": current_row,
                "description_column": ExcelGeneratorSettingsConstants.DESCRIPTION_COLUMN_FOR_REPORTS_IN_PROJECT.value,
                "hours_column": ExcelGeneratorSettingsConstants.HOURS_COLUMN_FOR_REPORTS_IN_PROJECT.value,
                "daily_hours_column": ExcelGeneratorSettingsConstants.DAILY_HOURS_COLUMN_FOR_REPORTS_IN_PROJECT.value,
            }
            fill_current_report_data(storage_data)
            current_row += 1
        summarizing_reports(
            worksheet,
            current_row,
            ExcelGeneratorSettingsConstants.HOURS_COLUMN_FOR_REPORTS_IN_PROJECT.value,
            ExcelGeneratorSettingsConstants.TOTAL_HOURS_FORMULA_REPORTS_IN_PROJECT.value,
        )
        if author != authors.last():
            workbook.create_sheet(index=0)
    return workbook


def convert_markdown_html_to_text(html: str) -> str:
    return "".join(BeautifulSoup(html).findAll(text=True))
