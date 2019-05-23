from openpyxl import Workbook
from openpyxl.cell import Cell
from openpyxl.styles import Alignment
from openpyxl.styles import Border
from openpyxl.styles import Font
from openpyxl.styles import Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

from employees.common.constants import ExcelGeneratorSettingsConstants
from managers.models import Project
from users.models import CustomUser


def set_format_styles_for_main_cells(cell: Cell, is_header: bool):
    cell.font = Font(name=ExcelGeneratorSettingsConstants.FONT.value, bold=True)
    cell.alignment = Alignment(horizontal=ExcelGeneratorSettingsConstants.CENTER_ALINGMENT.value)
    cell.border = (
        Border(bottom=Side(style=ExcelGeneratorSettingsConstants.BORDER.value))
        if is_header
        else Border(top=Side(style=ExcelGeneratorSettingsConstants.BORDER.value))
    )


def set_columns_width(worksheet: Worksheet, col_num: int, width_settings: list):
    column_letter = get_column_letter(col_num)
    column_dimensions = worksheet.column_dimensions[column_letter]
    column_dimensions.width = width_settings[col_num - 1]


def fill_headers(worksheet: Worksheet, headers: list, width_settings: list):
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
    cell.value = ExcelGeneratorSettingsConstants.TIMEVALUE_FORMULA.value.format(cell_value)
    cell.number_format = ExcelGeneratorSettingsConstants.HOURS_FORMAT.value


def fill_current_report_data(storage_data: dict):
    for col_num, cell_value in enumerate(storage_data["data"], 1):
        cell = storage_data["worksheet"].cell(row=storage_data["current_row"], column=col_num)
        if col_num == storage_data["description_column"]:
            set_and_fill_description_cell(cell, cell_value)
        elif col_num == storage_data["hours_column"]:
            set_and_fill_hours_cell(cell, cell_value)
        else:
            cell.value = cell_value


def summarizing_reports(worksheet: Worksheet, last_row: int, hours_column: int, formula: str):
    total_cell = worksheet.cell(row=last_row, column=ExcelGeneratorSettingsConstants.TOTAL_COLUMN.value)
    total_cell.value = ExcelGeneratorSettingsConstants.TOTAL.value
    set_format_styles_for_main_cells(total_cell, is_header=False)
    total_hours_cell = worksheet.cell(row=last_row, column=hours_column)
    total_hours_cell.value = formula.format(last_row - 1)
    total_hours_cell.number_format = ExcelGeneratorSettingsConstants.TOTAL_HOURS_FORMAT.value
    set_format_styles_for_main_cells(total_hours_cell, is_header=False)


def set_active_worksheet_name(workbook: Workbook, author: CustomUser) -> Worksheet:
    worksheet = workbook.active
    worksheet.title = f"{author.first_name} {author.last_name[0]}"
    return worksheet


def generate_xlsx_for_single_user(author: CustomUser) -> Workbook:
    reports = author.get_reports_created()
    workbook = Workbook()
    worksheet = set_active_worksheet_name(workbook, author)
    fill_headers(
        worksheet,
        ExcelGeneratorSettingsConstants.HEADERS_FOR_SINGLE_USER.value,
        ExcelGeneratorSettingsConstants.COLUMNS_WIDTH_FOR_SINGLE_USER.value,
    )
    current_row = ExcelGeneratorSettingsConstants.FIRST_ROW_FOR_DATA.value

    for report in reports:
        report_data = {
            "data": [
                report.date,
                report.project.name,
                report.task_activities.name,
                report.work_hours_str,
                report.description,
            ],
            "worksheet": worksheet,
            "current_row": current_row,
            "description_column": ExcelGeneratorSettingsConstants.DESCRIPTION_COLUMN_FOR_SINGLE_USER.value,
            "hours_column": ExcelGeneratorSettingsConstants.HOURS_COLUMN_FOR_SINGLE_USER.value,
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
    authors = project.members.all()
    workbook = Workbook()
    for author in authors:
        worksheet = set_active_worksheet_name(workbook, author)
        reports = author.projects.get(pk=project.pk).report_set.filter(author_id=author.pk)
        fill_headers(
            worksheet,
            ExcelGeneratorSettingsConstants.HEADERS_FOR_USER_IN_PROJECT.value,
            ExcelGeneratorSettingsConstants.COLUMNS_WIDTH_FOR_PROJECT.value,
        )

        current_row = ExcelGeneratorSettingsConstants.FIRST_ROW_FOR_DATA.value
        for report in reports:
            storage_data = {
                "data": [report.date, report.task_activities.name, report.work_hours_str, report.description],
                "worksheet": worksheet,
                "current_row": current_row,
                "description_column": ExcelGeneratorSettingsConstants.DESCRIPTION_COLUMN_FOR_REPORTS_IN_PROJECT.value,
                "hours_column": ExcelGeneratorSettingsConstants.HOURS_COLUMN_FOR_REPORTS_IN_PROJECT.value,
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
