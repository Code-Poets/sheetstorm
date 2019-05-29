import datetime
from decimal import Decimal

from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from freezegun import freeze_time
from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory

from employees.common.strings import ProjectReportListStrings
from employees.common.strings import ReportListStrings
from employees.models import Report
from employees.models import TaskActivityType
from employees.views import ProjectReportList
from employees.views import ReportDetail
from employees.views import ReportList
from employees.views import ReportViewSet
from employees.views import delete_report
from managers.models import Project
from users.models import CustomUser


class DataSetUpToTests(TestCase):
    def setUp(self):
        self.user = CustomUser(
            email="testuser@codepoets.it", password="newuserpasswd", first_name="John", last_name="Doe", country="PL"
        )
        self.user.full_clean()
        self.user.save()

        self.project = Project(name="Test Project", start_date=datetime.datetime.now())
        self.project.full_clean()
        self.project.save()

        self.report = Report(
            date=datetime.datetime.now().date(),
            description="Some description",
            author=self.user,
            project=self.project,
            work_hours=datetime.timedelta(hours=8),
            task_activities=TaskActivityType.objects.get(name="Other"),
        )
        self.report.full_clean()
        self.report.save()


class ReportListTests(DataSetUpToTests):
    def test_report_list_view_should_display_users_report_list_on_get(self):
        request = APIRequestFactory().get(path=reverse("report-list"))
        request.user = self.user
        response = ReportViewSet.as_view({"get": "list"})(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.report.description)

    def test_report_list_view_should_not_be_accessible_for_unauthenticated_user(self):
        request = APIRequestFactory().get(path=reverse("report-list"))
        request.user = AnonymousUser()
        response = ReportViewSet.as_view({"get": "list"})(request)
        self.assertEqual(response.status_code, 403)

    def test_report_list_view_should_not_display_other_users_reports(self):
        other_user = CustomUser(
            email="otheruser@codepoets.it", password="otheruserpasswd", first_name="Jane", last_name="Doe", country="PL"
        )
        other_user.full_clean()
        other_user.save()

        other_report = Report(
            date=datetime.datetime.now().date(),
            description="Some other description",
            author=other_user,
            project=self.project,
            work_hours=datetime.timedelta(hours=8),
            task_activities=TaskActivityType.objects.get(name="Other"),
        )
        other_report.full_clean()
        other_report.save()

        request = APIRequestFactory().get(path=reverse("report-list"))
        request.user = self.user
        response = ReportViewSet.as_view({"get": "list"})(request)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, other_report.description)

    def test_report_list_view_should_add_new_report_on_post(self):
        request = APIRequestFactory().post(
            path=reverse("report-list"),
            data={
                "date": datetime.datetime.now().date(),
                "description": "Some description",
                "project": self.project,
                "work_hours": "8:00",
                "task_activities": TaskActivityType.objects.get(name="Other"),
            },
        )
        request.user = self.user
        response = ReportViewSet.as_view({"post": "create"})(request)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Report.objects.all().count(), 2)


class ReportDetailTests(DataSetUpToTests):
    def test_report_detail_view_should_display_report_details_on_get(self):
        request = APIRequestFactory().get(path=reverse("report-detail", args=(self.report.pk,)))
        request.user = self.user
        response = ReportViewSet.as_view({"get": "retrieve"})(request, pk=self.report.pk)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.report.description)

    def test_report_list_view_should_not_be_accessible_for_unauthenticated_users(self):
        request = APIRequestFactory().get(path=reverse("report-detail", args=(self.report.pk,)))
        request.user = AnonymousUser()
        response = ReportViewSet.as_view({"get": "retrieve"})(request, pk=self.report.pk)
        self.assertEqual(response.status_code, 403)

    def test_report_detail_view_should_not_render_non_existing_report_on_get(self):
        request = APIRequestFactory().get(path=reverse("report-detail", args=(999,)))
        request.user = self.user
        response = ReportViewSet.as_view({"get": "retrieve"})(request, pk=999)
        self.assertEqual(response.status_code, 404)

    def test_report_detail_view_should_update_report_on_put(self):
        new_description = "Some other description"
        request = APIRequestFactory().put(
            path=reverse("report-detail", args=(self.report.pk,)),
            data={
                "date": datetime.datetime.now().date(),
                "description": new_description,
                "project": self.project,
                "work_hours": "8:00",
                "task_activities": TaskActivityType.objects.get(name="Other"),
            },
        )
        request.user = self.user
        response = ReportViewSet.as_view({"put": "update"})(request, pk=self.report.pk)
        current_description = Report.objects.get(pk=self.report.pk).description
        self.assertEqual(response.status_code, 200)
        self.assertEqual(current_description, new_description)

    def test_report_detail_view_should_delete_report_on_delete(self):
        request = APIRequestFactory().delete(path=reverse("report-detail", args=(self.report.pk,)))
        request.user = self.user
        response = ReportViewSet.as_view({"delete": "destroy"})(request, pk=self.report.pk)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Report.objects.all().count(), 0)


class ReportCustomListTests(TestCase):
    def setUp(self):
        self.user = CustomUser(
            email="testuser@codepoets.it", password="newuserpasswd", first_name="John", last_name="Doe", country="PL"
        )
        self.user.full_clean()
        self.user.save()

        self.project = Project(name="Test Project", start_date=datetime.datetime.now())
        self.project.full_clean()
        self.project.save()
        self.project.members.add(self.user)

        self.report = Report(
            date=datetime.datetime.now().date(),
            description="Some description",
            author=self.user,
            project=self.project,
            work_hours=datetime.timedelta(hours=8),
            task_activities=TaskActivityType.objects.get(name="Other"),
        )
        self.report.full_clean()
        self.report.save()
        self.url = reverse("custom-report-list")

    def test_custom_list_view_should_display_users_report_list_on_get(self):
        request = APIRequestFactory().get(path=self.url)
        request.user = self.user
        response = ReportList.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.report.description)
        reports = response.data["object_list"]
        self.assertTrue(self.report in reports)

    def test_custom_list_view_should_not_be_accessible_for_unauthenticated_user(self):
        request = APIRequestFactory().get(path=self.url)
        request.user = AnonymousUser()
        response = ReportList.as_view()(request)
        self.assertEqual(response.status_code, 403)

    def test_custom_list_view_should_not_display_other_users_reports(self):
        other_user = CustomUser(
            email="otheruser@codepoets.it", password="otheruserpasswd", first_name="Jane", last_name="Doe", country="PL"
        )
        other_user.full_clean()
        other_user.save()

        other_report = Report(
            date=datetime.datetime.now().date(),
            description="Some other description",
            author=other_user,
            project=self.project,
            work_hours=datetime.timedelta(hours=8),
            task_activities=TaskActivityType.objects.get(name="Other"),
        )
        other_report.full_clean()
        other_report.save()

        request = APIRequestFactory().get(path=self.url)
        request.user = self.user
        response = ReportList.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, other_report.description)

    def test_custom_report_list_view_should_add_new_report_on_post(self):
        request = APIRequestFactory().post(
            path=self.url,
            data={
                "date": datetime.datetime.now().date(),
                "description": "Some description",
                "project": self.project,
                "work_hours": "8:00",
                "task_activities": TaskActivityType.objects.get(name="Other"),
            },
        )
        request.user = self.user
        response = ReportList.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Report.objects.all().count(), 2)

    def test_custom_report_list_view_should_not_add_new_report_on_post_if_form_is_invalid(self):
        request = APIRequestFactory().post(
            path=self.url,
            data={"description": "Some description", "project": self.project, "work_hours": Decimal("8.00")},
        )
        request.user = self.user
        response = ReportList.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Report.objects.all().count(), 1)
        self.assertIsNotNone(response.data["errors"])

    def test_get_queryset_method_should_return_queryset_containing_all_of_current_users_reports(self):
        other_user = CustomUser(
            email="otheruser@codepoets.it", password="otheruserpasswd", first_name="Jane", last_name="Doe", country="PL"
        )
        other_user.full_clean()
        other_user.save()

        other_project = Project(name="Project test", start_date=datetime.datetime.now())
        other_project.full_clean()
        other_project.save()

        other_user_report = Report(
            date=datetime.datetime.now().date(),
            description="Some other description",
            author=other_user,
            project=self.project,
            work_hours=datetime.timedelta(hours=8),
            task_activities=TaskActivityType.objects.get(name="Other"),
        )
        other_user_report.full_clean()
        other_user_report.save()

        other_report_1 = Report(
            date=datetime.datetime.now().date(),
            description="Some other description",
            author=self.user,
            project=other_project,
            work_hours=datetime.timedelta(hours=8),
            task_activities=TaskActivityType.objects.get(name="Other"),
        )
        other_report_1.full_clean()
        other_report_1.save()

        other_report_2 = Report(
            date=datetime.date(2001, 1, 1),
            description="Some other description",
            author=self.user,
            project=self.project,
            work_hours=datetime.timedelta(hours=8),
            task_activities=TaskActivityType.objects.get(name="Other"),
        )
        other_report_2.full_clean()
        other_report_2.save()

        request = APIRequestFactory().get(path=self.url)
        request.user = self.user
        view = ReportList()
        view.request = request
        queryset = view.get_queryset()
        self.assertEqual(len(queryset), 3)
        self.assertFalse(other_user_report in queryset)
        self.assertEqual(queryset[0], other_report_1)
        self.assertEqual(queryset[1], self.report)
        self.assertEqual(queryset[2], other_report_2)

    def test_custom_report_list_add_project_method_should_register_current_user_as_project_member(self):
        new_project = Project(name="New Project", start_date=datetime.datetime.now())
        new_project.full_clean()
        new_project.save()
        request = APIRequestFactory().get(path=self.url)
        request.user = self.user
        view = ReportList()
        view.request = request
        view._add_project(new_project)
        self.assertTrue(self.user in new_project.members.all())

    def test_custom_report_list_create_serializer_method_should_return_serializer_with_project_field_options_containing_only_projects_to_which_current_user_belongs(
        self
    ):
        new_project = Project(name="New Project", start_date=datetime.datetime.now())
        new_project.full_clean()
        new_project.save()
        request = APIRequestFactory().get(path=self.url)
        request.user = self.user
        view = ReportList()
        view.request = request
        serializer = view._create_serializer()
        self.assertTrue(new_project not in serializer.fields["project"].queryset)
        self.assertTrue(self.project in serializer.fields["project"].queryset)

    def test_custom_report_list_create_serializer_method_should_return_serializer_with_date_field_containing_current_date(
        self
    ):
        request = APIRequestFactory().get(path=self.url)
        request.user = self.user
        view = ReportList()
        view.request = request
        with freeze_time("2010-01-21"):
            serializer = view._create_serializer()
            self.assertEqual(serializer.fields["date"].initial, "2010-01-21")

    def test_custom_report_list_create_serializer_method_should_return_serializer_filled_with_data_that_was_provided(
        self
    ):
        request = APIRequestFactory().post(
            path=self.url,
            data={
                "date": datetime.datetime.now().date(),
                "description": "Some description",
                "project": self.project,
                "work_hours": "8:00",
                "task_activities": TaskActivityType.objects.get(name="Other"),
            },
        )
        request.user = self.user
        view = ReportList()
        view.request = request
        serializer = view._create_serializer(data=request.POST)
        self.assertTrue(serializer.is_valid())

    def test_custom_report_list_view_should_add_user_to_project_selected_in_project_join_form_on_join(self):
        new_project = Project(name="New Project", start_date=datetime.datetime.now())
        new_project.full_clean()
        new_project.save()
        request = APIRequestFactory().post(path=self.url, data={"projects": new_project.id, "join": "join"})
        request.user = self.user
        response = ReportList.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.user in new_project.members.all())
        self.assertEqual(response.data["serializer"].fields["project"].initial, new_project)

    def test_custom_report_list_view_should_not_add_user_to_project_selected_in_project_join_form_on_post(self):
        new_project = Project(name="New Project", start_date=datetime.datetime.now())
        new_project.full_clean()
        new_project.save()
        request = APIRequestFactory().post(path=self.url, data={"projects": new_project.id})
        request.user = self.user
        response = ReportList.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.user in new_project.members.all())

    def test_custom_report_list_view_should_handle_no_project_being_selected_in_project_form_on_post(self):
        new_project = Project(name="New Project", start_date=datetime.datetime.now())
        new_project.full_clean()
        new_project.save()
        request = APIRequestFactory().post(path=self.url, data={"join": "join"})
        request.user = self.user
        response = ReportList.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_custom_report_list_view_should_dipslay_message_if_there_are_no_projects_available_to_join_to(self):
        request = APIRequestFactory().get(path=self.url)
        request.user = self.user
        response = ReportList.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(str(ReportListStrings.NO_PROJECTS_TO_JOIN.value) in str(response.render().content))

    def test_serializer_project_field_queryset_should_contain_only_projects_user_is_assigned_to_after_failed_post(self):
        new_project = Project(name="New Project", start_date=datetime.datetime.now())
        new_project.full_clean()
        new_project.save()
        request = APIRequestFactory().post(
            path=self.url,
            data={"description": "Some description", "project": self.project, "work_hours": Decimal("8.00")},
        )
        request.user = self.user
        response = ReportList.as_view()(request)
        project_field_choices = response.data["serializer"].fields["project"].choices.values()
        self.assertTrue(self.project.name in project_field_choices)
        self.assertFalse(new_project.name in project_field_choices)

    def test_serializer_project_field_queryset_should_contain_only_projects_user_is_assigned_to_after_project_join(
        self
    ):
        new_project_1 = Project(name="New Project", start_date=datetime.datetime.now())
        new_project_1.full_clean()
        new_project_1.save()
        new_project_2 = Project(name="New new Project", start_date=datetime.datetime.now())
        new_project_2.full_clean()
        new_project_2.save()
        request = APIRequestFactory().post(path=self.url, data={"projects": new_project_1.id, "join": "join"})
        request.user = self.user
        response = ReportList.as_view()(request)
        project_field_choices = response.data["serializer"].fields["project"].choices.values()
        self.assertTrue(self.project.name in project_field_choices)
        self.assertTrue(new_project_1.name in project_field_choices)
        self.assertFalse(new_project_2.name in project_field_choices)

    def test_serializer_project_field_queryset_should_contain_only_projects_user_is_assigned_to_after_failed_project_join(
        self
    ):
        new_project = Project(name="New Project", start_date=datetime.datetime.now())
        new_project.full_clean()
        new_project.save()
        request = APIRequestFactory().post(path=self.url, data={"join": "join"})
        request.user = self.user
        response = ReportList.as_view()(request)
        project_field_choices = response.data["serializer"].fields["project"].choices.values()
        self.assertTrue(self.project.name in project_field_choices)
        self.assertFalse(new_project.name in project_field_choices)


class ReportCustomDetailTests(TestCase):
    def setUp(self):
        self.user = CustomUser(
            email="testuser@codepoets.it", password="newuserpasswd", first_name="John", last_name="Doe", country="PL"
        )
        self.user.full_clean()
        self.user.save()

        self.project = Project(name="Test Project", start_date=datetime.datetime.now())
        self.project.full_clean()
        self.project.save()
        self.project.members.add(self.user)

        self.report = Report(
            date=datetime.datetime.now().date(),
            description="Some description",
            author=self.user,
            project=self.project,
            work_hours=datetime.timedelta(hours=8),
            task_activities=TaskActivityType.objects.get(name="Other"),
        )
        self.report.full_clean()
        self.report.save()

    def test_custom_report_detail_view_should_display_report_details_on_get(self):
        request = APIRequestFactory().get(path=reverse("custom-report-detail", args=(self.report.pk,)))
        request.user = self.user
        response = ReportDetail.as_view()(request, pk=self.report.pk)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.report.description)
        self.assertEqual(response.data["serializer"].instance, self.report)

    def test_custom_report_list_view_should_not_be_accessible_for_unauthenticated_users(self):
        request = APIRequestFactory().get(path=reverse("custom-report-detail", args=(self.report.pk,)))
        request.user = AnonymousUser()
        response = ReportDetail.as_view()(request, pk=self.report.pk)
        self.assertEqual(response.status_code, 403)

    def test_custom_report_detail_view_should_not_render_non_existing_report(self):
        request = APIRequestFactory().get(path=reverse("custom-report-detail", args=(999,)))
        request.user = self.user
        response = ReportDetail.as_view()(request, pk=999)
        self.assertEqual(response.status_code, 404)

    def test_custom_report_detail_view_should_update_report_on_post(self):
        new_description = "Some other description"
        request = APIRequestFactory().post(
            path=reverse("custom-report-detail", args=(self.report.pk,)),
            data={
                "date": datetime.datetime.now().date(),
                "description": new_description,
                "project": self.project,
                "work_hours": "8:00",
                "task_activities": TaskActivityType.objects.get(name="Other"),
            },
        )
        request.user = self.user
        response = ReportDetail.as_view()(request, pk=self.report.pk)
        self.report.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.report.description, new_description)

    def test_custom_report_detail_view_should_not_update_report_on_discard(self):
        new_description = "Some other description"
        request = APIRequestFactory().post(
            path=reverse("custom-report-detail", args=(self.report.pk,)),
            data={
                "date": datetime.datetime.now().date(),
                "description": new_description,
                "project": self.project,
                "work_hours": Decimal("8.00"),
                "discard": "Discard",
                "task_activities": TaskActivityType.objects.get(name="Other"),
            },
        )
        request.user = self.user
        response = ReportDetail.as_view()(request, pk=self.report.pk)
        self.report.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertNotEqual(self.report.description, new_description)

    def test_custom_report_detail_view_should_not_update_report_on_post_if_form_is_invalid(self):
        new_description = "Some other description"
        request = APIRequestFactory().post(
            path=reverse("custom-report-detail", args=(self.report.pk,)),
            data={"description": new_description, "project": self.project, "work_hours": Decimal("8.00")},
        )
        request.user = self.user
        response = ReportDetail.as_view()(request, pk=self.report.pk)
        self.report.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data["errors"])
        self.assertNotEqual(new_description, self.report.description)

    def test_custom_report_detail_view_should_not_update_report_if_author_is_not_a_member_of_selected_project(self):
        other_project = Project(name="Other Project", start_date=datetime.datetime.now())
        other_project.full_clean()
        other_project.save()
        new_description = "Some other description"
        request = APIRequestFactory().post(
            path=reverse("custom-report-detail", args=(self.report.pk,)),
            data={
                "date": datetime.datetime.now().date(),
                "description": new_description,
                "project": other_project,
                "work_hours": Decimal("8.00"),
                "task_activities": TaskActivityType.objects.get(name="Other"),
            },
        )
        request.user = self.user
        response = ReportDetail.as_view()(request, pk=self.report.pk)
        self.report.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["errors"]["project"][0].code, "does_not_exist")
        self.assertNotEqual(new_description, self.report.description)
        self.assertNotEqual(other_project, self.report.project)

    def test_custom_report_detail_view_project_field_should_not_display_projects_the_author_is_not_a_member_of(self):
        other_project = Project(name="Other Project", start_date=datetime.datetime.now())
        other_project.full_clean()
        other_project.save()
        request = APIRequestFactory().get(path=reverse("custom-report-detail", args=(self.report.pk,)))
        request.user = self.user
        response = ReportDetail.as_view()(request, pk=self.report.pk)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(other_project not in response.data["serializer"]._fields["project"].queryset)


class DeleteReportTests(TestCase):
    def setUp(self):
        self.user = CustomUser(
            email="testuser@codepoets.it", password="newuserpasswd", first_name="John", last_name="Doe", country="PL"
        )
        self.user.full_clean()
        self.user.save()

        self.project = Project(name="Test Project", start_date=datetime.datetime.now())
        self.project.full_clean()
        self.project.save()

        self.report = Report(
            date=datetime.datetime.now().date(),
            description="Some description",
            author=self.user,
            project=self.project,
            work_hours=datetime.timedelta(hours=8),
            task_activities=TaskActivityType.objects.get(name="Other"),
        )
        self.report.full_clean()
        self.report.save()

    def test_delete_report_view_should_delete_report_on_post(self):
        request = APIRequestFactory().delete(path=reverse("custom-report-delete", args=(self.report.pk,)))
        request.user = self.user
        response = delete_report(request, pk=self.report.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Report.objects.all().count(), 0)


class ProjectReportListTests(TestCase):
    def _assert_response_contain_report(self, response, reports):
        for report in reports:
            dates = ["creation_date", "last_update"]
            other_fields = ["description", "author", "task_activities"]
            work_hours = report.work_hours_str
            fields_to_check = [work_hours]
            for date in dates:
                fields_to_check.append(
                    datetime.datetime.strftime(
                        datetime.datetime.fromtimestamp(int(getattr(report, date).timestamp())), "%B %d, %Y, %-I:%M"
                    )
                )
            for field in other_fields:
                if field == "author":
                    fields_to_check.append(getattr(report, field).email)
                else:
                    fields_to_check.append(getattr(report, field))
            for field in fields_to_check:
                self.assertContains(response, field)

    def setUp(self):
        self.user = CustomUser(
            email="testuser@codepoets.it", password="newuserpasswd", first_name="John", last_name="Doe", country="PL"
        )
        self.user.full_clean()
        self.user.save()

        self.project = Project(name="Test Project", start_date=datetime.datetime.now())
        self.project.full_clean()
        self.project.save()
        self.project.members.add(self.user)

        self.report = Report(
            date=datetime.datetime.now().date(),
            description="Some description",
            author=self.user,
            project=self.project,
            work_hours=datetime.timedelta(hours=8),
        )
        self.report.full_clean()
        self.report.save()
        self.client.force_login(self.user)
        self.url = reverse("project-report-list", kwargs={"pk": self.project.pk})

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
        response = self.client.get(reverse("project-report-list", kwargs={"pk": 999}))
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

        request = APIRequestFactory().get(path=reverse("project-report-list", args=(self.project.pk,)))
        request.user = self.user
        response = ProjectReportList.as_view()(request, pk=self.project.pk)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, other_report.description)

    def test_project_report_list_view_should_display_message_if_project_has_no_reports(self):
        other_project = Project(name="Other Project", start_date=datetime.datetime.now())
        other_project.full_clean()
        other_project.save()
        response = self.client.get(reverse("project-report-list", kwargs={"pk": other_project.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, ProjectReportListStrings.NO_REPORTS_MESSAGE.value)

    def test_that_project_report_list_should_return_list_of_all_reports_assigned_to_project(self):
        other_user = CustomUser(
            email="otheruser@codepoets.it", password="otheruserpasswd", first_name="Jane", last_name="Doe", country="PL"
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
