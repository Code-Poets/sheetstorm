from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from employees.common.constants import ExcelGeneratorSettingsConstants
from employees.common.exports import generate_xlsx_for_project
from employees.common.exports import generate_xlsx_for_single_user
from employees.factories import ReportFactory
from employees.models import Report
from managers.factories import ProjectFactory
from users.factories import AdminUserFactory
from users.factories import ManagerUserFactory
from users.factories import UserFactory


class DataSetUpToTests(TestCase):
    def setUp(self):
        super().setUp()
        self.user = AdminUserFactory()
        self.project = ProjectFactory(
            name="aaa",
            start_date=timezone.now() + timezone.timedelta(days=1),
            stop_date=timezone.now() + timezone.timedelta(days=6),
        )
        self.report = ReportFactory(author=self.user, project=self.project)
        self.project.members.add(self.user)
        self.data = {"project": self.project.pk, "author": self.user.pk}
        self.url_single_user = reverse("export-data-xlsx", kwargs={"pk": self.user.pk})
        self.url_project = reverse("export-project-data-xlsx", kwargs={"pk": self.data["project"]})
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
            self.assertEqual(author, f"{self.user.first_name} {self.user.last_name[0]}")
        self.assertEqual(len(authors), 1)

    def test_date_should_be_the_same_in_excel(self):
        self.assertEqual(self.report.date, str(self.workbook_for_project.active.cell(row=2, column=1).value))

    def test_task_activity_should_be_the_same_in_excel(self):
        self.assertEqual(self.report.task_activities.name, self.workbook_for_project.active.cell(row=2, column=2).value)

    def test_hours_should_be_the_same_in_excel(self):
        work_hours = f"{self.report.work_hours_str}"
        self.assertEqual(
            ExcelGeneratorSettingsConstants.TIMEVALUE_FORMULA.value.format(work_hours),
            self.workbook_for_project.active.cell(row=2, column=3).value,
        )

    def test_description_should_be_the_same_in_excel(self):
        self.assertEqual(self.report.description, self.workbook_for_project.active.cell(row=2, column=4).value)


class ExportMethodTestForSingleUser(DataSetUpToTests):
    def test_sheetnames_should_have_name_and_first_letter_of_surname_and_one_sheet(self):
        sheet_names = self.workbook_for_user.get_sheet_names()
        for author in sheet_names:
            self.assertEqual(author, f"{self.user.first_name} {self.user.last_name[0]}")
        self.assertEqual(len(sheet_names), 1)

    def test_date_should_be_the_same_in_excel(self):
        self.assertEqual(self.report.date, str(self.workbook_for_user.active.cell(row=2, column=1).value))

    def test_project_name_should_be_the_same_in_excel(self):
        self.assertEqual(self.report.project.name, str(self.workbook_for_user.active.cell(row=2, column=2).value))

    def test_task_activity_should_be_the_same_in_excel(self):
        self.assertEqual(self.report.task_activities.name, self.workbook_for_user.active.cell(row=2, column=3).value)

    def test_hours_should_be_the_same_in_excel(self):
        work_hours = f"{self.report.work_hours_str}"
        self.assertEqual(
            ExcelGeneratorSettingsConstants.TIMEVALUE_FORMULA.value.format(work_hours),
            self.workbook_for_user.active.cell(row=2, column=4).value,
        )

    def test_description_should_be_the_same_in_excel(self):
        self.assertEqual(self.report.description, self.workbook_for_user.active.cell(row=2, column=5).value)


class TestExportingFunctions(TestCase):
    def setUp(self):
        super().setUp()
        self.employee = UserFactory()
        self.manager = ManagerUserFactory()
        self.project = ProjectFactory()
        self.project.members.add(self.employee)
        # creating reports in desc order
        for i in range(4, 0, -1):
            ReportFactory(author=self.employee, project=self.project, date=f"2019-06-{i}")
        self.report_asc = Report.objects.filter(author__id=self.employee.pk).order_by("-date")

    def test_that_unsorted_reported_will_be_sorted_asc_in_project_export(self):
        project_workbook = generate_xlsx_for_project(self.project)
        for i, element in enumerate(self.report_asc):
            self.assertEqual(project_workbook.active.cell(row=2 + i, column=1).value, element.date)

    def test_that_unsorted_reported_will_be_sorted_asc_in_user_export(self):
        project_workbook = generate_xlsx_for_single_user(self.employee)
        for i, element in enumerate(self.report_asc):
            self.assertEqual(project_workbook.active.cell(row=2 + i, column=1).value, element.date)