import datetime

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.shortcuts import reverse
from django.template.defaultfilters import date
from django.test import TestCase
from django.utils import timezone
from freezegun import freeze_time
from parameterized import parameterized

from employees.common.strings import AuthorReportListStrings
from employees.common.strings import ProjectReportListStrings
from employees.common.strings import ReportListStrings
from employees.common.strings import ReportValidationStrings
from employees.factories import ReportFactory
from employees.factories import TaskActivityTypeFactory
from employees.models import Report
from employees.models import TaskActivityType
from employees.views import AdminReportView
from employees.views import AuthorReportProjectView
from employees.views import AuthorReportView
from employees.views import ProjectReportList
from managers.factories import ProjectFactory
from managers.models import Project
from users.factories import AdminUserFactory
from users.factories import ManagerUserFactory
from users.factories import UserFactory
from users.models import CustomUser


class AuthorReportViewTests(TestCase):
    def setUp(self):
        super().setUp()
        self.user = AdminUserFactory()
        self.client.force_login(self.user)
        self.current_time = timezone.now()
        self.url = reverse(
            "author-report-list",
            kwargs={"pk": self.user.pk, "year": self.current_time.year, "month": self.current_time.month},
        )

    def test_author_reports_view_should_display_users_report_list_on_get(self):
        report = ReportFactory(author=self.user, date=timezone.now().date())
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

    def test_author_report_list_view_should_not_display_reports_from_another_month(self):
        report = ReportFactory(author=self.user, date=timezone.datetime(year=2018, month=9, day=1))
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, AuthorReportView.template_name)
        self.assertNotContains(response, report.project.name)

    def test_author_report_list_view_should_redirect_to_another_month_on_post(self):
        response = self.client.post(self.url, data={"date": "09-2020"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, reverse("author-report-list", kwargs={"pk": self.user.pk, "year": 2020, "month": 9})
        )

    def test_author_report_list_view_should_redirect_to_current_date_if_date_parameters_are_out_of_bonds(self):
        response = self.client.get(reverse("author-report-list", kwargs={"pk": self.user.pk, "year": 2019, "month": 4}))
        current_date = datetime.datetime.now()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse(
                "author-report-list",
                kwargs={"pk": self.user.pk, "year": current_date.year, "month": current_date.month},
            ),
        )

    def test_author_report_list_view_should_link_to_custom_report_detail_if_user_is_author(self):
        report = ReportFactory(author=self.user, date=timezone.now().date())
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, AuthorReportView.template_name)
        self.assertContains(response, reverse("custom-report-detail", kwargs={"pk": report.pk}))

    def test_author_report_list_view_should_link_to_admin_report_detail_if_user_is_author(self):
        report = ReportFactory(date=self.current_time)
        response = self.client.get(
            reverse(
                "author-report-list",
                kwargs={"pk": report.author.pk, "year": self.current_time.year, "month": self.current_time.month},
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, AuthorReportView.template_name)
        self.assertContains(response, reverse("admin-report-detail", kwargs={"pk": report.pk}))

    def test_author_report_list_view_should_display_monthly_hour_sum_in_hour_format(self):
        report_date = timezone.datetime(year=self.current_time.year, month=self.current_time.month, day=1)
        for i in range(4):
            ReportFactory(
                author=self.user, date=report_date + timezone.timedelta(days=i), work_hours=timezone.timedelta(hours=8)
            )

        response = self.client.get(self.url)

        self.assertContains(response, "32:00")
        self.assertNotContains(response, str(timezone.timedelta(hours=32)))


class AdminReportViewTests(TestCase):
    def setUp(self):
        super().setUp()
        self.admin = AdminUserFactory()
        self.user = UserFactory()
        self.task_activity = TaskActivityTypeFactory(is_default=True)
        self.project = ProjectFactory()
        self.project.members.add(self.user)
        self.client.force_login(self.admin)
        self.report = ReportFactory(author=self.user, project=self.project, task_activities=self.task_activity)
        self.url = reverse("admin-report-detail", kwargs={"pk": self.report.pk})
        self.data = {
            "date": timezone.now().date(),
            "description": "Some other description",
            "project": self.report.project.pk,
            "author": self.user.pk,
            "task_activities": self.task_activity.pk,
            "work_hours": "8:00",
            "current-project-pk": self.report.project.pk,
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


class ReportCustomListTests(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.force_login(self.user)
        self.task_activity = TaskActivityTypeFactory(is_default=True)
        self.report = ReportFactory(
            author=self.user,
            date=datetime.datetime.now().date(),
            task_activities=self.task_activity,
            work_hours=datetime.timedelta(hours=8),
        )
        self.report.project.members.add(self.user)
        self.url = reverse(
            "custom-report-list",
            kwargs={"year": datetime.datetime.now().date().year, "month": datetime.datetime.now().date().month},
        )
        self.data = {
            "date": datetime.datetime.now().date(),
            "description": "Some description",
            "project": self.report.project.pk,
            "author": self.user.pk,
            "work_hours": "8:00",
            "task_activities": self.task_activity.pk,
        }

    def test_custom_list_view_should_display_users_report_list_on_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.report.description)
        reports = response.context_data["object_list"]
        self.assertTrue(self.report in reports)

    def test_custom_list_view_should_not_display_other_users_reports(self):
        other_user = UserFactory()
        other_report = ReportFactory(author=other_user, project=self.report.project)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, other_report.description)

    def test_custom_list_view_should_not_display_other_users_reports_when_user_does_not_have_reports(self):
        user_with_no_reports = UserFactory()
        self.client.force_login(user_with_no_reports)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.report)

    def test_custom_report_list_view_should_add_new_report_on_post(self):
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Report.objects.all().count(), 2)

    def test_custom_report_list_view_should_add_user_to_project_selected_in_project_join_form_on_join(self):
        new_project = ProjectFactory(name="New Project", start_date=datetime.datetime.now())
        response = self.client.post(path=self.url, data={"projects": new_project.id, "join": "join"})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.user in new_project.members.all())

    def test_custom_report_list_view_should_not_add_user_to_project_selected_in_project_join_form_on_post(self):
        new_project = ProjectFactory(name="New Project", start_date=datetime.datetime.now())
        response = self.client.post(path=self.url, data={"projects": new_project.id})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.user in new_project.members.all())

    def test_custom_report_list_view_should_handle_no_project_being_selected_in_project_form_on_post(self):
        new_project = ProjectFactory(name="New Project", start_date=datetime.datetime.now())
        response = self.client.post(path=self.url, data={"join": "join"})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.user in new_project.members.all())

    def test_custom_report_list_view_should_dipslay_message_if_there_are_no_projects_available_to_join_to(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, str(ReportListStrings.NO_PROJECTS_TO_JOIN.value))

    def test_custom_report_list_view_should_redirect_to_another_month_if_month_switch_was_called_on_post(self):
        response = self.client.post(self.url, data={"date": "09-2020", "month-switch": "month-switch"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("custom-report-list", args=("2020", "9")))

    def test_custom_report_list_view_should_not_display_reports_from_different_month_than_selected(self):
        current_date = datetime.datetime.now().date()
        other_report = ReportFactory(
            date=current_date + relativedelta(months=+1), author=self.user, project=self.report.project
        )
        yet_another_report = ReportFactory(
            date=current_date + relativedelta(years=-1), author=self.user, project=self.report.project
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, other_report.description)
        self.assertNotContains(response, yet_another_report.description)

    def test_custom_report_list_view_form_should_have_latest_report_data_set(self):
        latest_activity = TaskActivityTypeFactory(name="Some other task activity")
        latest_report = ReportFactory(author=self.user, task_activities=latest_activity)
        latest_report.project.members.add(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.context_data["form"].initial["task_activities"].pk, latest_activity.pk)
        self.assertEqual(response.context_data["form"].initial["project"].pk, latest_report.project.pk)

    @parameterized.expand([(2019, 5, 1), (2019, 12, 31), (2020, 2, 29)])
    def test_report_create_form_default_date_should_be_today(self, year, month, day):
        with freeze_time("{:d}-{:02d}-{:02d}".format(year, month, day)):
            response = self.client.get(reverse("custom-report-list", kwargs={"year": year, "month": month}))
        self.assertEqual(
            response.context_data["form"].initial["date"], timezone.datetime(year=year, month=month, day=day)
        )

    def test_custom_report_list_view_task_activities_should_contain_only_task_activities_related_to_project(self):
        not_default_task_activity = TaskActivityTypeFactory()
        self.assertNotIn(not_default_task_activity, self.report.project.project_activities.all())

        response = self.client.get(self.url, data={"project": self.report.project.pk})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["form"].initial["project"], self.report.project)
        self.assertIn(self.task_activity, response.context["form"].fields["task_activities"].queryset)
        self.assertNotIn(not_default_task_activity, response.context["form"].fields["task_activities"].queryset)

    def test_custom_report_list_view_should_not_add_report_on_post_when_task_activity_is_not_related_not_project(self):
        not_related_to_project_task_activity = TaskActivityTypeFactory()
        author_reports_before_post = self.user.report_set.all()

        self.data["task_activities"] = not_related_to_project_task_activity.pk

        response = self.client.post(self.url, self.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context_data["form"].errors["task_activities"][0],
            ReportValidationStrings.TASK_ACTIVITY_NOT_RELATED_TO_PROJECT.value,
        )
        self.assertCountEqual(author_reports_before_post, self.user.report_set.all())

    def test_custom_report_list_should_contains_in_form_only_active_projects_related_to_user(self):
        other_project = ProjectFactory()

        response = self.client.get(self.url)
        project_choices = response.context["form"].fields["project"].queryset

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.report.project, project_choices)
        self.assertNotIn(other_project, project_choices)
        self.assertIn(self.report.project, Project.objects.filter_active())

    def test_custom_report_list_should_have_empty_queryset_for_project_and_task_activities_when_he_is_not_in_any_active_project(
        self
    ):
        self.user.projects.remove(self.report.project)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["form"].fields["project"].queryset), 0)
        self.assertEqual(len(response.context["form"].fields["task_activities"].queryset), 0)

    def test_custom_report_list_manager_should_have_displayed_projects_to_choose_where_he_is_only_a_manager(self):
        manager = ManagerUserFactory()
        self.client.force_login(manager)
        self.report.project.managers.add(manager)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.report.project, response.context["form"].fields["project"].queryset)

    def test_custom_report_list_view_should_display_monthly_hour_sum_in_hour_format(self):
        report_date = timezone.datetime(year=timezone.now().year, month=timezone.now().month, day=1)
        for i in range(3):
            ReportFactory(
                author=self.user, date=report_date + timezone.timedelta(days=i), work_hours=timezone.timedelta(hours=8)
            )

        response = self.client.get(self.url)

        self.assertContains(response, "32:00")
        self.assertNotContains(response, str(timezone.timedelta(hours=32)))


class ProjectReportDetailTests(TestCase):
    def setUp(self):
        super().setUp()
        self.user = AdminUserFactory()
        self.task_activity = TaskActivityTypeFactory(is_default=True)
        self.project = ProjectFactory()
        self.project.members.add(self.user)
        self.client.force_login(self.user)
        self.report = ReportFactory(author=self.user, project=self.project, task_activities=self.task_activity)
        self.url = reverse("project-report-detail", args=(self.report.pk,))
        self.data = {
            "date": self.report.date,
            "description": self.report.description,
            "project": self.report.project.pk,
            "author": self.report.author.pk,
            "task_activities": self.task_activity.pk,
            "work_hours": self.report.work_hours_str,
            "current-project-pk": self.report.project.pk,
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

    def test_project_report_detail_view_should_show_data_from_current_report_not_from_latest_report(self):
        # Latest report
        ReportFactory(author=self.user)
        response = self.client.get(path=reverse("custom-report-detail", args=(self.report.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data["form"].initial["task_activities"], self.report.task_activities.pk)
        self.assertEqual(response.context_data["form"].initial["project"], self.report.project.pk)


class ReportDetailViewTests(TestCase):
    def setUp(self):
        super().setUp()
        self.user = UserFactory()
        self.client.force_login(self.user)
        self.task_activity = TaskActivityTypeFactory(is_default=True)
        self.project = ProjectFactory()
        self.project.members.add(self.user)
        self.report = ReportFactory(author=self.user, project=self.project, task_activities=self.task_activity)
        self.url = reverse("custom-report-detail", args=(self.report.pk,))
        self.data = {
            "date": self.report.date,
            "description": self.report.description,
            "project": self.project.pk,
            "author": self.report.author.pk,
            "task_activities": self.task_activity.pk,
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
        self.data["project"] = ""
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

    def test_custom_report_detail_view_should_show_data_from_current_report_not_from_latest_report(self):
        # Latest report
        ReportFactory(author=self.user)
        response = self.client.get(path=reverse("custom-report-detail", args=(self.report.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data["form"].initial["task_activities"], self.report.task_activities.pk)
        self.assertEqual(response.context_data["form"].initial["project"], self.report.project.pk)

    def test_manager_should_be_able_to_update_his_reports_in_project_in_which_he_is_not_manager(self):
        user_manager = ManagerUserFactory()
        self.client.force_login(user_manager)
        report_manager = ReportFactory(author=user_manager, task_activities=self.task_activity)
        report_manager.project.members.add(user_manager)
        data = {
            "date": report_manager.date,
            "description": "report_manager other description",
            "project": report_manager.project.pk,
            "author": report_manager.author.pk,
            "task_activities": self.task_activity.pk,
            "work_hours": report_manager.work_hours_str,
        }
        response = self.client.post(path=reverse("custom-report-detail", args=(report_manager.pk,)), data=data)
        report_manager.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(report_manager.description, data["description"])

    def test_custom_report_detail_view_should_return_only_one_report_when_are_more_than_one_managers_in_project(self):
        manager_1 = ManagerUserFactory()
        manager_2 = ManagerUserFactory()
        self.report.project.managers.add(manager_1)
        self.report.project.managers.add(manager_2)
        report_1 = ReportFactory(author=manager_1, project=self.report.project)
        self.client.force_login(manager_1)
        response = self.client.get(path=reverse("custom-report-detail", args=(report_1.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, report_1.description)

    def test_custom_report_detail_view_should_contains_in_project_field_all_project_related_with_user(self):
        other_user_project = ProjectFactory()
        other_user_project.members.add(self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(self.user.projects.all(), response.context_data["form"].fields["project"].queryset)

    def test_custom_report_detail_view_should_contains_chosen_project_even_user_is_no_longer_in_project(self):
        other_user_project = ProjectFactory()
        other_user_project.members.add(self.user)
        self.user.projects.remove(self.report.project)

        response = self.client.get(self.url)

        self.assertIn(self.report.project, response.context_data["form"].fields["project"].queryset)


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


class ProjectReportListTests(TestCase):
    def setUp(self):
        super().setUp()
        self.task_type = TaskActivityType(pk=1, name="Other", is_default=True)
        self.task_type.full_clean()
        self.task_type.save()
        self.user = AdminUserFactory()
        self.project = ProjectFactory()
        self.project.members.add(self.user)
        self.client.force_login(self.user)
        current_date = datetime.datetime.now().date()
        self.report = ReportFactory(
            author=self.user,
            project=self.project,
            date=current_date,
            task_activities=self.task_type,
            work_hours=datetime.timedelta(hours=8),
        )
        self.data = {
            "date": timezone.now().date(),
            "description": "Some other description",
            "project": self.report.project.pk,
            "author": self.user.pk,
            "task_activities": self.report.task_activities.pk,
            "work_hours": "8.00",
        }
        self.year = current_date.year
        self.month = current_date.month
        self.url = reverse(
            "project-report-list", kwargs={"pk": self.project.pk, "year": self.year, "month": self.month}
        )

    def test_project_report_list_view_should_display_projects_report_list_on_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, ProjectReportList.template_name)
        self.assertContains(response, self.project.name)
        self._assert_response_contain_report(response, [self.report])

    def test_project_report_list_view_should_not_be_accessible_for_unauthenticated_user(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_project_report_list_view_should_not_display_non_existing_projects_reports(self):
        response = self.client.get(
            reverse("project-report-list", kwargs={"pk": 999, "year": self.year, "month": self.month})
        )
        self.assertEqual(response.status_code, 404)

    def test_project_report_list_view_should_not_display_other_projects_reports(self):
        other_project = Project(name="Other Project", start_date=datetime.datetime.now())
        other_project.full_clean()
        other_project.save()

        other_report = Report(
            date=datetime.datetime.now().date(),
            description="Some other description",
            author=self.user,
            project=other_project,
            work_hours=datetime.timedelta(hours=8),
        )
        other_report.full_clean()
        other_report.save()

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, other_report.description)

    def test_project_report_list_view_should_display_message_if_project_has_no_reports(self):
        other_project = Project(name="Other Project", start_date=datetime.datetime.now())
        other_project.full_clean()
        other_project.save()
        response = self.client.get(
            reverse("project-report-list", kwargs={"pk": other_project.pk, "year": self.year, "month": self.month})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, ProjectReportListStrings.NO_REPORTS_MESSAGE.value)

    def test_that_project_report_list_should_return_list_of_all_reports_assigned_to_project(self):
        other_user = CustomUser(
            email="otheruser@codepoets.it",
            password="otheruserpasswd",
            first_name="Jane",
            last_name="Doe",
            is_active=True,
        )
        other_user.full_clean()
        other_user.save()
        self.project.members.add(other_user)

        other_project = Project(name="Project test", start_date=datetime.datetime.now())
        other_project.full_clean()
        other_project.save()
        other_project.members.add(self.user)
        other_project.members.add(other_user)

        other_project_report = Report(
            date=datetime.datetime.now().date(),
            description="Some other description",
            author=self.user,
            project=other_project,
            work_hours=datetime.timedelta(hours=8),
        )
        other_project_report.full_clean()
        other_project_report.save()

        other_report_1 = Report(
            date=datetime.datetime.now().date(),
            description="Some other description",
            author=other_user,
            project=self.project,
            work_hours=datetime.timedelta(hours=8),
        )
        other_report_1.full_clean()
        other_report_1.save()

        other_report_2 = Report(
            date=datetime.date(2001, 1, 1),
            description="Some other description",
            author=self.user,
            project=self.project,
            work_hours=datetime.timedelta(hours=8),
        )
        other_report_2.full_clean()
        other_report_2.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, ProjectReportList.template_name)
        self.assertContains(response, self.project.name)
        self._assert_response_contain_report(response, [self.report, other_report_1, other_report_2])

    def test_project_report_list_view_should_not_display_reports_from_different_month_than_specified(self):
        current_date = datetime.datetime.now().date()
        other_report = Report(
            date=current_date + relativedelta(years=-1),
            description="Some other description",
            author=self.user,
            project=self.project,
            work_hours=datetime.timedelta(hours=8),
        )
        other_report.full_clean()
        other_report.save()

        yet_another_report = Report(
            date=current_date + relativedelta(years=-1),
            description="Yet another description",
            author=self.user,
            project=self.project,
            work_hours=datetime.timedelta(hours=8),
        )
        yet_another_report.full_clean()
        yet_another_report.save()

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, other_report.description)
        self.assertNotContains(response, yet_another_report.description)

    def test_project_report_list_view_should_redirect_to_another_month_on_post(self):
        response = self.client.post(self.url, data={"date": "09-2020"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, reverse("project-report-list", kwargs={"pk": self.project.id, "year": 2020, "month": 9})
        )

    def test_project_report_list_view_should_redirect_to_current_date_if_date_parameters_are_out_of_bonds(self):
        response = self.client.get(
            reverse("project-report-list", kwargs={"pk": self.project.pk, "year": 2019, "month": 4})
        )
        current_date = datetime.datetime.now()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse(
                "project-report-list",
                kwargs={"pk": self.project.id, "year": current_date.year, "month": current_date.month},
            ),
        )

    def test_project_report_list_view_should_display_inactive_members_reports(self):
        current_date = datetime.datetime.now().date()
        previous_date = current_date + relativedelta(months=-1)
        inactive_user = UserFactory(is_active=False)

        project_report = ReportFactory(
            author=inactive_user, date=current_date, project=self.project, description="This is for current project."
        )
        other_project_report = ReportFactory(
            author=inactive_user, date=current_date, description="This is for other project."
        )
        project_report_from_other_month = ReportFactory(
            author=inactive_user, date=previous_date, project=self.project, description="This is for another month."
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, project_report.description)
        self.assertNotContains(response, other_project_report.description)
        self.assertNotContains(response, project_report_from_other_month.description)

        response = self.client.get(
            reverse(
                "project-report-list",
                kwargs={"pk": self.project.pk, "year": previous_date.year, "month": previous_date.month},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, project_report.description)
        self.assertNotContains(response, other_project_report.description)
        self.assertContains(response, project_report_from_other_month.description)

    def _assert_response_contain_report(self, response, reports):
        for report in reports:
            dates = ["creation_date", "last_update"]
            other_fields = ["description", "author", "task_activities"]
            work_hours = report.work_hours_str
            fields_to_check = [work_hours]
            for date_ in dates:
                fields_to_check.append(date(getattr(report, date_), settings.DATE_FORMAT))
            for field in other_fields:
                if field == "author":
                    fields_to_check.append(getattr(report, field).get_full_name())
                else:
                    fields_to_check.append(getattr(report, field))
            for field in fields_to_check:
                self.assertContains(response, field)

    def test_project_report_list_view_should_display_monthly_hour_sum_in_hour_format(self):
        report_date = timezone.datetime(year=self.year, month=self.month, day=1)
        for i in range(3):
            ReportFactory(
                author=self.user,
                project=self.project,
                date=report_date + timezone.timedelta(days=i),
                work_hours=timezone.timedelta(hours=8),
            )

        response = self.client.get(self.url)

        self.assertContains(response, "32:00")
        self.assertNotContains(response, str(timezone.timedelta(hours=32)))


class TestAuthorReportProjectView(TestCase):
    def setUp(self):
        super().setUp()
        self.user = UserFactory()
        self.project = ProjectFactory()
        self.project.members.add(self.user)
        current_date = timezone.now()
        self.report = ReportFactory(author=self.user, project=self.project, date=current_date)

        self.url = reverse(
            "author-report-project-list",
            kwargs={
                "pk": self.project.pk,
                "user_pk": self.user.pk,
                "year": current_date.year,
                "month": current_date.month,
            },
        )

    def test_view_should_display_author_reports_of_project_on_admin_get(self):
        admin = AdminUserFactory()
        self.client.force_login(admin)
        response = self.client.get(self.url)
        self.assertContains(response, self.report.description)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, AuthorReportProjectView.template_name)

    def test_view_should_display_author_reports_of_project_on_manager_project_get(self):
        manager = ManagerUserFactory()
        self.project.managers.add(manager)
        self.client.force_login(manager)
        response = self.client.get(self.url)
        self.assertContains(response, self.report.description)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, AuthorReportProjectView.template_name)

    def test_view_should_not_display_reports_for_any_other_managers(self):
        user = ManagerUserFactory()
        other_project = ProjectFactory()
        other_project.managers.add(user)
        self.client.force_login(user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_view_should_not_display_reports_for_other_users(self):
        employee_user = UserFactory()
        self.client.force_login(employee_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_view_should_display_author_reports_only_one_project(self):
        admin = AdminUserFactory()
        report_from_project1 = ReportFactory(author=self.user, project=self.project, date=self.report.date)
        report_from_other_project = ReportFactory(author=self.user)
        self.client.force_login(admin)
        response = self.client.get(self.url)
        self.assertContains(response, self.report.description)
        self.assertContains(response, report_from_project1.description)
        self.assertContains(response, report_from_project1.project.name)
        self.assertNotContains(response, report_from_other_project.description)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, AuthorReportProjectView.template_name)


class ReportSummaryTests(TestCase):
    def setUp(self):
        self.user = ManagerUserFactory()
        project_1 = ProjectFactory()
        project_1.members.add(self.user)
        project_2 = ProjectFactory()
        project_2.managers.add(self.user)
        self.projects = [project_1, project_2]
        self.current_time = timezone.now()
        self.hours_per_report = 4
        self.total_hours = 160
        self._generate_user_reports_for_current_and_previous_month_with_uneven_total_hours()
        self.expected_work_hours_stats = self._get_total_hours_per_project_and_percentage_from_month()

    def test_report_list_should_accurately_evaluate_work_hours_statistics(self):
        self.client.force_login(self.user)
        url = reverse("custom-report-list", kwargs={"year": self.current_time.year, "month": self.current_time.month})

        context_data = self.client.get(url).context_data
        self._assert_projects_work_percentage_is_evaluated_accurately(context_data)

    def test_author_report_list_should_accurately_evaluate_work_hours_statistics(self):
        admin_user = AdminUserFactory()
        self.client.force_login(admin_user)
        url = reverse(
            "author-report-list",
            kwargs={"pk": self.user.pk, "year": self.current_time.year, "month": self.current_time.month},
        )

        context_data = self.client.get(url).context_data

        self._assert_projects_work_percentage_is_evaluated_accurately(context_data)

    def _assert_projects_work_percentage_is_evaluated_accurately(self, context_data):
        self.assertTrue("projects_work_percentage" in context_data.keys())

        projects_work_percentage = context_data["projects_work_percentage"]

        self.assertEqual(self.expected_work_hours_stats, projects_work_percentage)

    def _generate_user_reports_for_current_and_previous_month_with_uneven_total_hours(self):
        reports_per_project, remaining_hours = self._strip_hours_between_projects()

        months_and_reported_days = self._get_number_of_reported_days_for_each_month(reports_per_project)

        for start_date, total_reported_days in months_and_reported_days.items():
            total_reported_days = reports_per_project
            report_date = start_date
            for _ in range(total_reported_days):
                work_hours = timezone.timedelta(hours=self.hours_per_report)
                for project in self.projects:
                    ReportFactory(project=project, author=self.user, work_hours=work_hours, date=report_date)
                report_date += relativedelta(days=1)
            if remaining_hours != 0:
                ReportFactory(
                    project=self.projects[0],
                    author=self.user,
                    work_hours=timezone.timedelta(hours=remaining_hours),
                    date=report_date,
                )

    def _get_number_of_reported_days_for_each_month(self, reports_per_project, difference_ratio=2):
        current_month_start_date = self.current_time.replace(day=1)
        previous_month_start_date = current_month_start_date + relativedelta(months=-1)
        return {
            previous_month_start_date: reports_per_project // difference_ratio,
            current_month_start_date: reports_per_project,
        }

    def _strip_hours_between_projects(self):
        hours_per_project = self.total_hours // len(self.projects)
        remaining_hours = self.total_hours % len(self.projects)
        reports_per_project = hours_per_project // self.hours_per_report
        remaining_hours += hours_per_project % self.hours_per_report
        return reports_per_project, remaining_hours

    def _get_total_hours_per_project_and_percentage_from_month(self):
        reports_per_project, remaining_hours = self._strip_hours_between_projects()
        first_project_total_hours = timezone.timedelta(
            hours=reports_per_project * self.hours_per_report + remaining_hours
        )
        other_projects_total_hours = timezone.timedelta(hours=reports_per_project * self.hours_per_report)
        hours_and_percentage_per_project = {}
        total_hours_timedelta = timezone.timedelta(hours=self.total_hours)
        for project in self.projects:
            if project is self.projects[0]:
                hours_and_percentage_per_project.update(
                    {project.name: (first_project_total_hours, first_project_total_hours / total_hours_timedelta * 100)}
                )
            else:
                hours_and_percentage_per_project.update(
                    {
                        project.name: (
                            other_projects_total_hours,
                            other_projects_total_hours / total_hours_timedelta * 100,
                        )
                    }
                )
        return dict(sorted(hours_and_percentage_per_project.items()))
