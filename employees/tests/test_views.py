import datetime

from django.shortcuts import reverse
from django.test import TestCase
from django.utils import timezone

from employees.common.strings import AuthorReportListStrings
from employees.factories import ReportFactory
from employees.models import TaskActivityType
from employees.models import Report
from employees.views import AdminReportView
from employees.views import AuthorReportView
from managers.factories import ProjectFactory
from managers.models import Project
from users.factories import UserFactory


class InitTaskTypeTestCase(TestCase):
    def setUp(self):
        task_type = TaskActivityType(pk=1, name="Other")
        task_type.full_clean()
        task_type.save()


class AuthorReportViewTests(InitTaskTypeTestCase):
    def setUp(self):
        super().setUp()
        self.user = UserFactory()
        self.client.force_login(self.user)
        self.url = reverse("author-report-list", kwargs={"pk": self.user.pk})

    def test_author_reports_view_should_display_users_report_list_on_get(self):
        report = ReportFactory(author=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, AuthorReportView.template_name)
        self.assertContains(response, report.project.name)

    def test_author_report_list_view_should_not_display_other_users_reports(self):
        report = ReportFactory()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, AuthorReportView.template_name)
        self.assertNotContains(response, report.project.name)

    def test_author_report_list_view_should_display_message_if_user_has_no_reports(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, AuthorReportView.template_name)
        self.assertContains(response, AuthorReportListStrings.NO_REPORTS_MESSAGE.value)


class AdminReportViewTests(InitTaskTypeTestCase):
    def setUp(self):
        super().setUp()
        self.user = UserFactory()
        self.project = ProjectFactory()
        self.project.members.add(self.user)
        self.client.force_login(self.user)
        self.report = ReportFactory(author=self.user, project=self.project)
        self.url = reverse("admin-report-detail", kwargs={"pk": self.report.pk})
        self.data = {
            "date": timezone.now().date(),
            "description": "Some other description",
            "project": self.report.project.pk,
            "author": self.user.pk,
            "task_activities": self.report.task_activities.pk,
            "work_hours": "8:00",
        }

    def test_admin_report_detail_view_should_display_report_details(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, AdminReportView.template_name)
        self.assertContains(response, self.report.project.name)

    def test_admin_report_detail_view_should_update_report_on_post(self):
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 302)
        self.report.refresh_from_db()
        self.assertEqual(self.report.description, self.data["description"])
        self.assertEqual(self.report.author, self.user)
        self.assertTrue(self.report.editable)


class ProjectReportDetailTests(InitTaskTypeTestCase):
    def setUp(self):
        super().setUp()
        self.user = UserFactory()
        self.project = ProjectFactory()
        self.project.members.add(self.user)
        self.client.force_login(self.user)
        self.report = ReportFactory(author=self.user, project=self.project)
        self.url = reverse("project-report-detail", args=(self.report.pk,))
        self.data = {
            "date": self.report.date,
            "description": self.report.description,
            "project": self.report.project.pk,
            "author": self.report.author.pk,
            "task_activities": self.report.task_activities.pk,
            "work_hours": self.report.work_hours_str,
        }

    def test_project_report_detail_view_should_display_report_details(self):
        response = self.client.get(path=self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.report.description)
        self.assertEqual(response.context_data["form"].instance, self.report)

    def test_project_report_list_view_should_not_be_accessible_for_unauthenticated_user(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_project_report_detail_view_should_update_report_on_post(self):
        self.data["description"] = "Some other description"
        response = self.client.post(path=self.url, data=self.data)
        self.report.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.report.description, self.data["description"])
        self.assertTrue(self.report.editable)

    def test_project_report_detail_view_should_not_update_report_on_post_if_form_is_invalid(self):
        self.data["description"] = ""
        response = self.client.post(path=self.url, data=self.data)
        self.report.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context_data["form"]._errors)
        self.assertTrue(self.report.editable)


class ReportDetailViewTests(TestCase):
    def setUp(self):
        super().setUp()
        self.task_type = TaskActivityType(pk=1, name="Other")
        self.task_type.full_clean()
        self.task_type.save()
        self.user = UserFactory()
        self.project = ProjectFactory()
        self.project.members.add(self.user)
        self.client.force_login(self.user)
        self.report = ReportFactory(author=self.user, project=self.project)
        self.url = reverse("custom-report-detail", args=(self.report.pk,))
        self.data = {
            "date": self.report.date,
            "description": self.report.description,
            "project": self.report.project.pk,
            "author": self.report.author,
            "task_activities": self.report.task_activities.pk,
            "work_hours": self.report.work_hours_str,
        }

    def test_custom_report_detail_view_should_display_report_details_on_get(self):
        response = self.client.get(path=reverse("custom-report-detail", args=(self.report.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.report.description)

    def test_custom_report_list_view_should_not_be_accessible_for_unauthenticated_users(self):
        self.client.logout()
        response = self.client.get(path=reverse("custom-report-detail", args=(self.report.pk,)))
        self.assertEqual(response.status_code, 302)

    def test_custom_report_detail_view_should_not_render_non_existing_report(self):
        response = self.client.get(path=reverse("custom-report-detail", args=(999,)))
        self.assertEqual(response.status_code, 404)

    def test_custom_report_detail_view_should_update_report_on_post(self):
        self.data["description"] = "Some other description"
        response = self.client.post(path=self.url, data=self.data)
        self.report.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.report.description, self.data["description"])

    def test_custom_report_detail_view_should_not_update_report_on_post_if_form_is_invalid(self):
        old_description = self.data["description"]
        self.data["description"] = "Some other description"
        self.data["project"] = None
        response = self.client.post(path=self.url, data=self.data)
        self.report.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context_data["form"].errors)
        self.assertEqual(old_description, self.report.description)

    def test_custom_report_detail_view_should_not_update_report_if_author_is_not_a_member_of_selected_project(self):
        other_project = ProjectFactory()
        other_project.full_clean()
        other_project.save()
        old_description = self.data["description"]
        self.data["description"] = "Some other description"
        old_project = self.data["project"]
        self.data["project"] = other_project.pk
        response = self.client.post(path=self.url, data=self.data)
        self.report.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context_data["form"].errors)
        self.assertEqual(old_description, self.report.description)
        self.assertEqual(old_project, self.report.project.pk)

    def test_custom_report_detail_view_project_field_should_not_display_projects_the_author_is_not_a_member_of(self):
        other_project = Project(name="Other Project", start_date=datetime.datetime.now())
        other_project.full_clean()
        other_project.save()
        response = self.client.get(path=reverse("custom-report-detail", args=(self.report.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(other_project not in response.context_data["form"].fields["project"].queryset)


class ReportDeleteViewTests(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.force_login(self.user)
        self.report = ReportFactory(author=self.user)
        self.url = reverse("custom-report-delete", args=(self.report.pk,))

    def test_delete_report_view_should_delete_report_on_post(self):
        response = self.client.post(path=self.url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Report.objects.filter(pk=self.report.pk).exists())
