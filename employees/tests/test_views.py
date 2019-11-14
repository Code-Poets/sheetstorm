import datetime

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.shortcuts import reverse
from django.template.defaultfilters import date
from django.test import TestCase
from django.utils import timezone
from freezegun import freeze_time

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
            author=self.user, date=datetime.datetime.now().date(), task_activities=self.task_activity
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

    def test_default_date_should_be_first_day_of_the_month_if_there_are_no_reports(self):
        response = self.client.get(reverse("custom-report-list", kwargs={"year": 2019, "month": 5}))
        self.assertEqual(response.context_data["form"].initial["date"], datetime.date(year=2019, month=5, day=1))

    def test_default_date_should_be_monday_when_the_last_report_was_created_on_friday_of_the_same_month(self):
        # Friday
        with freeze_time("2019-05-03"):
            ReportFactory(date=datetime.date(year=2019, month=5, day=3), author=self.user)
        # Monday
        with freeze_time("2019-5-06"):
            response = self.client.get(reverse("custom-report-list", kwargs={"year": 2019, "month": 5}))
        self.assertEqual(response.context_data["form"].initial["date"], datetime.date(year=2019, month=5, day=6))

    def test_default_date_should_be_day_later_than_last_report_if_it_wasnt_created_today(self):
        with freeze_time("2019-05-01"):
            ReportFactory(date=datetime.date(year=2019, month=5, day=1), author=self.user)
        with freeze_time("2019-05-03"):
            response = self.client.get(reverse("custom-report-list", kwargs={"year": 2019, "month": 5}))
        self.assertEqual(response.context_data["form"].initial["date"], datetime.date(year=2019, month=5, day=2))

    def test_default_date_should_be_last_day_of_the_month_if_thats_the_date_of_last_report(self):
        with freeze_time("2019-05-31"):
            report = ReportFactory(date=datetime.date(year=2019, month=5, day=31), author=self.user)
        with freeze_time("2019-06-01"):
            response = self.client.get(reverse("custom-report-list", kwargs={"year": 2019, "month": 5}))
        self.assertEqual(response.context_data["form"].initial["date"], report.date)

    def test_default_date_should_be_date_of_the_last_report_if_it_was_created_today(self):
        with freeze_time("2019-05-01"):
            report = ReportFactory(date=datetime.date(year=2019, month=5, day=1), author=self.user)
            response = self.client.get(reverse("custom-report-list", kwargs={"year": 2019, "month": 5}))
        self.assertEqual(response.context_data["form"].initial["date"], report.date)

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
            author=self.user, project=self.project, date=current_date, task_activities=self.task_type
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
