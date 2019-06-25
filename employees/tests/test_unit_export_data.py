from datetime import timedelta
from io import BytesIO

from django.db.models import Sum
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from freezegun import freeze_time
from openpyxl import load_workbook

from employees.common.constants import ExcelGeneratorSettingsConstants
from employees.common.exports import generate_xlsx_for_project
from employees.common.exports import generate_xlsx_for_single_user
from employees.common.exports import get_employee_name
from employees.factories import ReportFactory
from employees.models import Report
from managers.factories import ProjectFactory
from users.factories import AdminUserFactory
from users.factories import ManagerUserFactory
from users.factories import UserFactory


@freeze_time("2019-06-24")
class DataSetUpToTests(TestCase):
    def setUp(self):
        super().setUp()
        self.user = AdminUserFactory()
        self.project_start_date = timezone.now() + timezone.timedelta(days=-1)
        self.project = ProjectFactory(
            name="aaa", start_date=self.project_start_date, stop_date=timezone.now() + timezone.timedelta(days=6)
        )
        self.report = ReportFactory(author=self.user, project=self.project)
        self.project.members.add(self.user)
        self.data = {"project": self.project.pk, "author": self.user.pk}
        self.url_single_user = reverse(
            "export-data-xlsx",
            kwargs={
                "pk": self.user.pk,
                "year": str(self.report.creation_date.year),
                "month": str(self.report.creation_date.month),
            },
        )
        self.url_project = reverse(
            "export-project-data-xlsx",
            kwargs={
                "pk": self.data["project"],
                "year": str(self.report.creation_date.year),
                "month": str(self.report.creation_date.month),
            },
        )
        self.workbook_for_project = generate_xlsx_for_project(self.project)
        self.workbook_for_user = generate_xlsx_for_single_user(self.user)


class ExportViewTest(DataSetUpToTests):
    def test_export_reports_should_download_for_single_user_if_he_is_logged(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url_single_user)
        self.assertEqual(response.status_code, 200)

    def test_export_reports_should_not_download_data_if_he_is_not_logged(self):
        response = self.client.get(self.url_single_user)
        self.assertEqual(response.status_code, 302)

    def test_export_reports_for_project_should_download_if_user_is_logged(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url_project)
        self.assertEqual(response.status_code, 200)

    def test_export_reports_for_project_should_not_download_if_user_is_not_logged(self):
        response = self.client.get(self.url_project)
        self.assertEqual(response.status_code, 302)


class ExportMethodTestForProject(DataSetUpToTests):
    def test_sheetnames_should_have_name_and_first_letter_of_surname_and_one_sheet(self):
        authors = self.workbook_for_project.get_sheet_names()
        for author in authors:
            self.assertEqual(author, f"{self.user.first_name} {self.user.last_name[0]}.")
        self.assertEqual(len(authors), 1)

    def test_date_should_be_the_same_in_excel(self):
        self.assertEqual(
            self.report.date,
            str(
                self.workbook_for_project.active.cell(
                    row=ExcelGeneratorSettingsConstants.FIRST_ROW_FOR_DATA.value, column=1
                ).value
            ),
        )

    def test_task_activity_should_be_the_same_in_excel(self):
        self.assertEqual(
            self.report.task_activities.name,
            self.workbook_for_project.active.cell(
                row=ExcelGeneratorSettingsConstants.FIRST_ROW_FOR_DATA.value, column=3
            ).value,
        )

    def test_hours_should_be_the_same_in_excel(self):
        work_hours = f"{self.report.work_hours_str}"
        self.assertEqual(
            ExcelGeneratorSettingsConstants.TIMEVALUE_FORMULA.value.format(work_hours),
            self.workbook_for_project.active.cell(
                row=ExcelGeneratorSettingsConstants.FIRST_ROW_FOR_DATA.value, column=4
            ).value,
        )

    def test_description_should_be_the_same_in_excel(self):
        self.assertEqual(
            self.report.description,
            self.workbook_for_project.active.cell(
                row=ExcelGeneratorSettingsConstants.FIRST_ROW_FOR_DATA.value, column=5
            ).value,
        )

    def test_daily_hours_should_be_equal_to_sum_of_hours_from_reports_of_author(self):
        employee1 = UserFactory()
        employee2 = UserFactory()
        self.project.members.add(employee1)
        self.project.members.add(employee2)
        employees = [employee1, employee2]
        for i in range(3):
            ReportFactory(
                author=employee1, project=self.project, work_hours=timedelta(hours=i + 1), date=timezone.now()
            )
        for i in range(3):
            ReportFactory(
                author=employee2, project=self.project, work_hours=timedelta(hours=i + 2), date=timezone.now()
            )

        project_workbook = generate_xlsx_for_project(self.project)

        for employee in employees:
            author = get_employee_name(employee)
            sheet = project_workbook.get_sheet_by_name(author)
            daily_hours_for_employee = sheet.cell(
                row=ExcelGeneratorSettingsConstants.FIRST_ROW_FOR_DATA.value, column=2
            ).value

            sum_from_reports = employee.report_set.aggregate(Sum("work_hours"))
            sum_from_reports_as_string = self._hours_date_time_to_excel_time_field(sum_from_reports["work_hours__sum"])
            self.assertEqual(daily_hours_for_employee, sum_from_reports_as_string)

    @staticmethod
    def _hours_date_time_to_excel_time_field(hours_delta):
        sum_from_reports_as_string = f"{int(hours_delta.total_seconds() / 3600)}:00:00"
        return f'=timevalue("{sum_from_reports_as_string}")'


class ExportMethodTestForSingleUser(DataSetUpToTests):
    def test_sheetnames_should_have_name_and_first_letter_of_surname_and_one_sheet(self):
        sheet_names = self.workbook_for_user.get_sheet_names()
        for author in sheet_names:
            self.assertEqual(author, f"{self.user.first_name} {self.user.last_name[0]}.")
        self.assertEqual(len(sheet_names), 1)

    def test_date_should_be_the_same_in_excel(self):
        self.assertEqual(
            self.report.date,
            str(
                self.workbook_for_user.active.cell(
                    row=ExcelGeneratorSettingsConstants.FIRST_ROW_FOR_DATA.value, column=1
                ).value
            ),
        )

    def test_project_name_should_be_the_same_in_excel(self):
        self.assertEqual(
            self.report.project.name,
            str(
                self.workbook_for_user.active.cell(
                    row=ExcelGeneratorSettingsConstants.FIRST_ROW_FOR_DATA.value, column=3
                ).value
            ),
        )

    def test_task_activity_should_be_the_same_in_excel(self):
        self.assertEqual(
            self.report.task_activities.name,
            self.workbook_for_user.active.cell(
                row=ExcelGeneratorSettingsConstants.FIRST_ROW_FOR_DATA.value, column=4
            ).value,
        )

    def test_hours_should_be_the_same_in_excel(self):
        work_hours = f"{self.report.work_hours_str}"
        self.assertEqual(
            ExcelGeneratorSettingsConstants.TIMEVALUE_FORMULA.value.format(work_hours),
            self.workbook_for_user.active.cell(
                row=ExcelGeneratorSettingsConstants.FIRST_ROW_FOR_DATA.value, column=5
            ).value,
        )

    def test_description_should_be_the_same_in_excel(self):
        self.assertEqual(
            self.report.description,
            self.workbook_for_user.active.cell(
                row=ExcelGeneratorSettingsConstants.FIRST_ROW_FOR_DATA.value, column=6
            ).value,
        )


class TestExportingFunctions(TestCase):
    def setUp(self):
        super().setUp()
        self.employee1 = UserFactory(first_name="Cezar", last_name="Goldstein")
        self.employee2 = UserFactory(first_name="", last_name="", email="bozydar.stolzman@codepots.it")
        self.employee3 = UserFactory(first_name="Abimelek", last_name="Zuckerberg")
        self.manager = ManagerUserFactory()
        self.project = ProjectFactory()
        self.project.members.add(self.employee1)
        self.project.members.add(self.employee2)
        self.project.members.add(self.employee3)
        reports_in_day = 2
        # creating reports in desc order
        number_of_days = 4
        self.year = "2019"
        self.month = "06"
        for i in range(number_of_days, 0, -1):
            for _ in range(reports_in_day):
                ReportFactory(author=self.employee2, project=self.project, date=f"{self.year}-{self.month}-{i}")
                ReportFactory(author=self.employee3, project=self.project, date=f"{self.year}-{self.month}-{i}")
                ReportFactory(author=self.employee1, project=self.project, date=f"{self.year}-{self.month}-{i}")
        self.report_asc = Report.objects.filter(author__id=self.employee1.pk).order_by("date")
        self.reports_per_user = reports_in_day * number_of_days

    def test_unsorted_reports_will_be_sorted_asc_by_first_name_and_asc_by_date_in_project_export(self):
        project_workbook = generate_xlsx_for_project(self.project)
        for j, sheet in enumerate(project_workbook.worksheets):
            # Check that sheets are sorted in ascending order, according to employee's first name / user email
            self.assertEqual(sheet.title, get_employee_name(getattr(self, f"employee{3 - j}")))
            self._assert_reports_are_sorted_in_ascending_order(project_workbook)
            self._assert_dates_are_unique_in_reports_of_user(project_workbook)

    def test_project_members_with_no_report_will_be_skipped_in_project_export(self):
        not_a_member = UserFactory(first_name="Asterix", last_name="Longsword")
        self.project.members.add(not_a_member)
        project_workbook = generate_xlsx_for_project(self.project)
        employee_name = get_employee_name(not_a_member)
        self.assertNotIn(employee_name, [s.title for s in project_workbook.worksheets])

    def test_unsorted_reports_will_be_sorted_asc_by_date_in_user_export(self):
        user_workbook = generate_xlsx_for_single_user(self.employee1)
        self._assert_reports_are_sorted_in_ascending_order(user_workbook)
        self._assert_dates_are_unique_in_reports_of_user(user_workbook)

    def _assert_reports_are_sorted_in_ascending_order(self, workbook):
        for i, element in enumerate(self.report_asc):
            # there are two reports per day, but "Date" and "Daily hours" should occur only once per day
            if i % 2 == 0:
                self.assertEqual(
                    workbook.active.cell(
                        row=ExcelGeneratorSettingsConstants.FIRST_ROW_FOR_DATA.value + i, column=1
                    ).value,
                    element.date,
                )
                self.assertIn(
                    "=timevalue",
                    workbook.active.cell(
                        row=ExcelGeneratorSettingsConstants.FIRST_ROW_FOR_DATA.value + i, column=2
                    ).value,
                )
            else:
                self.assertEqual(
                    workbook.active.cell(
                        row=ExcelGeneratorSettingsConstants.FIRST_ROW_FOR_DATA.value + i, column=1
                    ).value,
                    None,
                )
                self.assertEqual(
                    workbook.active.cell(
                        row=ExcelGeneratorSettingsConstants.FIRST_ROW_FOR_DATA.value + i, column=2
                    ).value,
                    None,
                )

    def _assert_dates_are_unique_in_reports_of_user(self, workbook):
        for worksheet in workbook.worksheets:
            dates = []
            for i in range(self.reports_per_user):
                cell_value = worksheet.cell(
                    row=ExcelGeneratorSettingsConstants.FIRST_ROW_FOR_DATA.value + i, column=1
                ).value
                if cell_value is not None:
                    dates.append(cell_value)
            number_of_dates = len(dates)
            number_of_unique_dates = len(set(dates))
            self.assertTrue(number_of_dates > 0)
            self.assertEqual(number_of_dates, number_of_unique_dates)

    def test_user_can_export_only_his_own_reports(self):
        self.client.force_login(self.employee1)
        url = reverse("export-data-xlsx", kwargs={"pk": self.employee2.pk, "year": self.year, "month": self.month})
        response = self.client.get(url)
        received_workbook = load_workbook(filename=BytesIO(response.content))
        self.assertEqual(len(received_workbook.sheetnames), 1)
        self.assertEqual(received_workbook.sheetnames[0], f"{self.employee1.first_name} {self.employee1.last_name[0]}.")
