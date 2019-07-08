import csv
from datetime import timedelta
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from bs4 import BeautifulSoup
from django.utils import timezone
from django.utils.datetime_safe import datetime
from openpyxl import Workbook
from openpyxl.cell import Cell
from openpyxl.cell.cell import TYPE_FORMULA
from openpyxl.styles import Alignment
from openpyxl.styles import Border
from openpyxl.styles import Font
from openpyxl.styles import Side
from openpyxl.utils import get_column_letter

from common.convert import convert_string_work_hours_field_to_hour_and_minutes
from employees.common.constants import ExcelGeneratorSettingsConstants as constants
from employees.models import Report
from employees.models import ReportQuerySet
from managers.models import Project
from users.models import CustomUser


def set_format_styles_for_main_cells(cell: Cell, is_header: bool) -> None:
    cell.font = Font(name=constants.FONT.value, bold=True)
    cell.alignment = Alignment(horizontal=constants.CENTER_ALINGMENT.value)
    border_style = Side(style=constants.BORDER.value)
    cell.border = (
        Border(bottom=border_style, top=border_style, right=border_style, left=border_style)
        if is_header
        else Border(top=border_style)
    )


def set_and_fill_description_cell(cell: Cell, cell_value: str) -> None:
    wrapped_alignment = Alignment(vertical=constants.VERCTICAL_TOP.value, wrap_text=True)
    cell.alignment = wrapped_alignment
    cell.value = cell_value


def set_and_fill_hours_cell(cell: Cell, cell_value: str) -> None:
    if cell_value is not None:
        cell.value = constants.TIMEVALUE_FORMULA.value.format(cell_value)
    else:
        cell.value = cell_value
    cell.number_format = constants.HOURS_FORMAT.value


def get_employee_name(author: CustomUser) -> str:
    if author.last_name and author.first_name:
        return f"{author.first_name} {author.last_name[0]}."
    else:
        return f"{author.email}"


def generate_xlsx_for_single_user(author: CustomUser) -> Workbook:
    return ReportExtractor().generate_xlsx_for_single_user(author)


def generate_xlsx_for_project(project: Project) -> Workbook:
    return ReportExtractor().generate_xlsx_for_project(project)


class ReportExtractor:
    def __init__(self) -> None:
        self._current_row = -1
        self._workbook = None  # type: Workbook
        self._headers = []  # type: List
        self._description_column_index = -1
        self._hours_column_index = -1
        self._daily_hours_column_index = -1
        self._formula = ""
        self._last_date = None
        self._active_worksheet = None  # type: Workbook
        self._headers_settings = {}  # type: Dict

    def generate_xlsx_for_project(self, project: Project) -> Workbook:
        authors = project.members.all()
        self._workbook = Workbook()
        self._set_xlsx_settings_for_project_report()
        for author in authors:
            employee_name = get_employee_name(author)
            reports = project.report_set.filter(author=author.pk).order_by("date")
            if not reports:
                continue

            self._fill_report_for_single_user(employee_name, reports)

        self._workbook._sheets.sort(key=lambda w: str.lower(w.title))
        return self._workbook

    def generate_xlsx_for_single_user(self, author: CustomUser) -> Workbook:
        reports = author.get_reports_created().order_by("date", "project__name")  # type: ReportQuerySet
        self._workbook = Workbook()
        self._set_xlsx_settings_for_user_report()
        employee_name = get_employee_name(author)

        self._fill_report_for_single_user(employee_name, reports)
        return self._workbook

    def _fill_report_for_single_user(self, employee_name: str, reports: ReportQuerySet) -> None:
        self._prepare_worksheet(employee_name)
        for report in reports:
            self._fill_single_report(report, reports)

        self._summarize_user_reports()

    def _fill_single_report(self, report: Report, reports: ReportQuerySet) -> None:
        report_date, daily_hours = self._get_report_date_and_daily_hours(report, reports)
        storage_data = {
            constants.DATE_HEADER_STR.value: report_date,
            constants.DAILY_HOURS_HEADER_STR.value: daily_hours,
            constants.PROJECT_HEADER_STR.value: report.project.name,
            constants.TASK_ACTIVITY_HEADER_STR.value: report.task_activities.name,
            constants.HOURS_HEADER_STR.value: report.work_hours_str,
            constants.DESCRIPTION_HEADER_STR.value: convert_markdown_html_to_text(report.markdown_description),
        }
        self._fill_current_report_data(storage_data)
        self._current_row += 1

    def _prepare_worksheet(self, employee_name: str) -> None:
        self._reset_per_sheet_settings()
        self._set_active_worksheet_name(employee_name)
        self._fill_headers(employee_name)

    def _reset_per_sheet_settings(self) -> None:
        self._current_row = constants.FIRST_ROW_FOR_DATA.value
        self._last_date = None

    def _set_xlsx_settings_for_project_report(self) -> None:
        self._formula = constants.TOTAL_HOURS_FORMULA_REPORTS_IN_PROJECT.value
        self._headers_settings = dict(constants.HEADERS_TO_COLUMNS_SETTINGS_FOR_USER_IN_PROJECT.value)
        self._headers = [k for k, v in self._headers_settings.items() if v is not None]

    def _set_xlsx_settings_for_user_report(self) -> None:
        self._formula = constants.TOTAL_HOURS_FORMULA_FOR_SINGLE_USER.value
        self._headers_settings = dict(constants.HEADERS_TO_COLUMNS_SETTINGS_FOR_SINGLE_USER.value)
        self._headers = [k for k, v in self._headers_settings.items() if v is not None]

    def _set_active_worksheet_name(self, employee_name: str) -> None:
        if self._workbook.active.title != "Sheet":
            self._set_employees_worksheet_active(employee_name)
        self._active_worksheet = self._workbook.active
        self._active_worksheet.title = employee_name

    def _set_employees_worksheet_active(self, employee_name: str) -> None:
        try:
            employee_sheet_index = self._workbook.worksheets.index(employee_name)
        except ValueError:
            self._workbook.create_sheet()
            employee_sheet_index = -1
        self._workbook.active = self._workbook.worksheets[employee_sheet_index]

    def _fill_headers(self, employee_name: str) -> None:
        self._set_employee_name_in_worksheet(employee_name)
        for col_num, column_name in enumerate(self._headers, start=1):
            cell = self._active_worksheet.cell(row=constants.HEADERS_ROW.value, column=col_num)
            cell.value = column_name
            set_format_styles_for_main_cells(cell, is_header=True)
            self._set_column_width(col_num, column_name)

    def _set_employee_name_in_worksheet(self, employee_name: str) -> None:
        self._active_worksheet.merge_cells(
            start_row=constants.EMPLOYEE_NAME_ROW.value,
            end_row=constants.EMPLOYEE_NAME_ROW.value,
            start_column=constants.EMPLOYEE_NAME_START_COLUMN.value,
            end_column=constants.EMPLOYEE_NAME_END_COLUMN.value,
        )
        cell = self._active_worksheet.cell(
            row=constants.EMPLOYEE_NAME_ROW.value, column=constants.EMPLOYEE_NAME_START_COLUMN.value
        )
        cell.value = constants.EMPLOYEE_NAME.value.format(employee_name)

    def _set_column_width(self, col_num: int, column_name: str) -> None:
        column_letter = get_column_letter(col_num)
        column_dimensions = self._active_worksheet.column_dimensions[column_letter]
        column_dimensions.width = self._headers_settings[column_name].width

    def _fill_current_report_data(self, storage_data: dict) -> None:
        for column_name, cell_value in storage_data.items():
            if self._headers_settings[column_name] is not None:
                cell = self._active_worksheet.cell(
                    row=self._current_row, column=self._headers_settings[column_name].position
                )
                if column_name == constants.DESCRIPTION_HEADER_STR.value:
                    set_and_fill_description_cell(cell, cell_value)
                elif column_name == constants.HOURS_HEADER_STR.value:
                    set_and_fill_hours_cell(cell, cell_value)
                elif column_name == constants.DAILY_HOURS_HEADER_STR.value:
                    set_and_fill_hours_cell(cell, cell_value)
                else:
                    cell.value = cell_value

    def _summarize_user_reports(self) -> None:
        total_cell = self._active_worksheet.cell(row=self._current_row, column=constants.TOTAL_COLUMN.value)
        total_cell.value = constants.TOTAL.value
        for column_number in range(1, self._active_worksheet.max_column + 1):
            set_format_styles_for_main_cells(
                self._active_worksheet.cell(row=self._current_row, column=column_number), is_header=False
            )

        total_hours_cell = self._active_worksheet.cell(
            row=self._current_row, column=self._headers_settings[constants.HOURS_HEADER_STR.value].position
        )
        total_hours_cell.value = self._formula.format(self._current_row - 1)
        total_hours_cell.number_format = constants.TOTAL_HOURS_FORMAT.value
        set_format_styles_for_main_cells(total_hours_cell, is_header=False)

    def _get_report_date_and_daily_hours(
        self, current_report: Report, reports_subset: ReportQuerySet
    ) -> Tuple[Optional[datetime], Optional[timedelta]]:
        # returns report_date and daily_hours
        # if this is their first occurrence in a day
        # other way returns None
        date = current_report.date
        if self._last_date == date:
            daily_hours = None
            report_date = None
        else:
            daily_hours = reports_subset.get_report_work_hours_sum_for_date(date)
            report_date = date
        self._last_date = date
        return (report_date, daily_hours)


def convert_markdown_html_to_text(html: str) -> str:
    return "".join(BeautifulSoup(html, features="html.parser").findAll(text=True))


def save_work_book_as_csv(writer: csv.DictWriter, work_book: Workbook) -> None:
    sheet = work_book.active
    is_last_row = False
    total_hours = timezone.timedelta()

    for row_number, row in enumerate(sheet.rows, start=1):
        if row_number == 1:
            continue

        # Check if is last row by comparing first cell value to `TOTAL`.
        if isinstance(row[0].value, str) and row[0].value == constants.TOTAL.value:
            is_last_row = True

        next_row = []
        for cell_number, cell in enumerate(row, start=1):
            if isinstance(cell.value, str) and cell.value.lower().startswith("=timevalue"):
                hours_as_string = cell.value[len('=timevalue("') : -len('")')]  # noqa: E203
                next_row.append(hours_as_string)

                # If contains valid hours value, add it to total hours.
                if (
                    not is_last_row
                    and row_number > 2
                    and cell_number
                    == constants.HEADERS_TO_COLUMNS_SETTINGS_FOR_SINGLE_USER.value[
                        constants.HOURS_HEADER_STR.value
                    ].position
                ):
                    hours, minutes = convert_string_work_hours_field_to_hour_and_minutes(hours_as_string)
                    total_hours += timezone.timedelta(hours=int(hours), minutes=int(minutes))
            elif is_last_row and cell.data_type is TYPE_FORMULA:
                next_row.append(str(total_hours)[:-3])
            else:
                next_row.append(cell.value)

        writer.writerow(next_row)
