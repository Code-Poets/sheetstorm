from django.shortcuts import reverse
from django.test import TestCase
from django.utils import timezone

from employees.common.strings import AuthorReportListStrings
from employees.factories import ReportFactory
from employees.views import AdminReportView
from employees.views import AuthorReportView
from users.factories import UserFactory


class AuthorReportViewTests(TestCase):
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


class AdminReportViewTests(TestCase):
    def setUp(self):
        super().setUp()
        self.user = UserFactory()
        self.client.force_login(self.user)
        self.report = ReportFactory(author=self.user)
        self.url = reverse("admin-report-detail", kwargs={"pk": self.report.pk})
        self.data = {
            "date": timezone.now().date(),
            "description": "Some other description",
            "project": self.report.project.pk,
            "author": self.user.pk,
            "task_activities": self.report.task_activities.pk,
            "work_hours": "8.00",
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
