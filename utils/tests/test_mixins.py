from django.test import RequestFactory
from django.test import TestCase
from django.utils import timezone
from django.views.generic import DetailView
from django.views.generic import ListView
from freezegun import freeze_time

from employees.factories import ReportFactory
from employees.models import Report
from managers.factories import ProjectFactory
from managers.models import Project
from users.factories import UserFactory
from users.models import CustomUser
from utils.mixins import ProjectsWorkPercentageMixin
from utils.mixins import UserIsAuthorOfCurrentReportMixin
from utils.mixins import UserIsManagerOfCurrentProjectMixin
from utils.mixins import UserIsManagerOfCurrentReportProjectOrAuthorOfCurrentReportMixin


class UserIsAuthorOfCurrentReportMixinTestCase(TestCase):
    def setUp(self):
        super().setUp()

        class TestView(UserIsAuthorOfCurrentReportMixin, ListView):
            model = Report

        self.view = TestView.as_view()
        self.request_factory = RequestFactory()

    def test_user_is_author_of_current_report_mixin_should_limit_view_report_queryset_if_user_is_employee(self):
        user = UserFactory(user_type=CustomUser.UserType.EMPLOYEE.name)

        author_report = ReportFactory(author=user)
        # Other author report.
        ReportFactory()

        assert Report.objects.count() == 2

        request = self.request_factory.get("anything")
        request.user = user
        response = self.view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context_data["object_list"]), 1)
        self.assertEqual(response.context_data["object_list"][0].pk, author_report.pk)

    def test_user_is_author_of_current_report_mixin_should_not_limit_view_report_queryset_if_user_is_not_employee(self):
        user = UserFactory(user_type=CustomUser.UserType.MANAGER.name)

        ReportFactory(author=user)
        # Other author report.
        ReportFactory()

        assert Report.objects.count() == 2

        request = self.request_factory.get("anything")
        request.user = user
        response = self.view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context_data["object_list"]), 2)


class UserIsManagerOfCurrentProjectMixinTestCase(TestCase):
    def setUp(self):
        super().setUp()

        class TestView(UserIsManagerOfCurrentProjectMixin, ListView):
            model = Project

        self.view = TestView.as_view()
        self.request_factory = RequestFactory()

    def test_user_is_manager_of_current_project_mixin_should_limit_view_project_queryset_if_user_is_manager(self):
        user = UserFactory(user_type=CustomUser.UserType.MANAGER.name)

        manager_project = ProjectFactory()
        manager_project.managers.add(user)
        # Project without current user as manager.
        ProjectFactory()

        assert Project.objects.count() == 2

        request = self.request_factory.get("anything")
        request.user = user
        response = self.view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context_data["object_list"]), 1)
        self.assertEqual(response.context_data["object_list"][0].pk, manager_project.pk)

    def test_user_is_manager_of_current_project_mixin_should_not_limit_view_project_queryset_if_user_is_not_manager(
        self
    ):
        user = UserFactory(user_type=CustomUser.UserType.EMPLOYEE.name)

        manager_project = ProjectFactory()
        manager_project.managers.add(user)
        # Project without current user as manager.
        ProjectFactory()

        assert Project.objects.count() == 2

        request = self.request_factory.get("anything")
        request.user = user
        response = self.view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context_data["object_list"]), 2)


class UserIsManagerOfCurrentReportProjectOrAuthorOfCurrentReportMixinTestCase(TestCase):
    def setUp(self):
        super().setUp()

        class TestView(UserIsManagerOfCurrentReportProjectOrAuthorOfCurrentReportMixin, ListView):
            model = Report

        self.view = TestView.as_view()
        self.request_factory = RequestFactory()

    def test_user_is_manager_of_current_project_or_author_of_current_report_mixin_should_limit_view_project_queryset_if_user_is_manager(
        self
    ):
        user = UserFactory(user_type=CustomUser.UserType.MANAGER.name)

        report = ReportFactory()
        report.project.managers.add(user)
        # Report with project without current user as manager.
        ReportFactory()

        assert Report.objects.count() == 2

        request = self.request_factory.get("anything")
        request.user = user
        response = self.view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context_data["object_list"]), 1)
        self.assertEqual(response.context_data["object_list"][0].pk, report.pk)

    def test_user_is_manager_of_current_project_or_author_of_current_report_mixin_should_not_limit_view_project_queryset_if_user_is_not_manager(
        self
    ):
        user = UserFactory(user_type=CustomUser.UserType.EMPLOYEE.name)

        report = ReportFactory()
        report.project.managers.add(user)
        # Report with project without current user as manager.
        ReportFactory()

        assert Report.objects.count() == 2

        request = self.request_factory.get("anything")
        request.user = user
        response = self.view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context_data["object_list"]), 2)


@freeze_time("2019-11-06 21:00:00")
class ProjectsWorkPercentageMixinTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.request_factory = RequestFactory()
        self.request = self.request_factory.get("anything")
        self.request.user = UserFactory()

    def test_project_work_percentage_mixin_should_pass_work_hours_summary_to_report_list_view(self):
        class TestView(ProjectsWorkPercentageMixin, ListView):
            model = Report

        report_1 = ReportFactory()
        report_2 = ReportFactory()

        response = TestView.as_view()(self.request)

        self.assertEqual(response.status_code, 200)
        self.assertTrue("projects_work_percentage" in response.context_data.keys())
        projects_work_percentage = response.context_data["projects_work_percentage"]
        self.assertTrue(report_1.project.name in projects_work_percentage)
        self.assertTrue(report_2.project.name in projects_work_percentage)

    def test_project_work_percentage_mixin_should_pass_work_hours_summary_to_user_detail_view(self):
        class TestView(ProjectsWorkPercentageMixin, DetailView):
            model = CustomUser

        user = UserFactory()
        report_1 = ReportFactory(author=user)
        report_2 = ReportFactory(author=user)
        report_3 = ReportFactory()

        response = TestView.as_view()(self.request, pk=user.pk)

        self.assertEqual(response.status_code, 200)
        self.assertTrue("projects_work_percentage" in response.context_data.keys())
        projects_work_percentage = response.context_data["projects_work_percentage"]
        self.assertTrue(report_1.project.name in projects_work_percentage.keys())
        self.assertTrue(report_2.project.name in projects_work_percentage.keys())
        self.assertFalse(report_3.project.name in projects_work_percentage.keys())


class TestGetProjectsWorkPercentage(TestCase):
    def setUp(self):
        super().setUp()
        self.user = UserFactory()
        self.project_1 = ProjectFactory()
        self.project_2 = ProjectFactory()

    def test_get_projects_work_hours_and_percentage_should_return_dictionary_containing_with_work_time_and_time_percent_per_project(
        self
    ):
        ReportFactory(author=self.user, project=self.project_1, work_hours=timezone.timedelta(hours=8))
        ReportFactory(author=self.user, project=self.project_2, work_hours=timezone.timedelta(hours=4))
        ReportFactory(author=self.user, project=self.project_2, work_hours=timezone.timedelta(hours=8))
        ReportFactory(project=self.project_1, work_hours=timezone.timedelta(hours=4))

        result = ProjectsWorkPercentageMixin()._get_projects_work_hours_and_percentage(self.user.report_set.all())

        self.assertEqual(len(result), 2)
        self.assertEqual(
            result,
            {
                self.project_1.name: (timezone.timedelta(hours=8), 40.0),
                self.project_2.name: (timezone.timedelta(hours=12), 60.0),
            },
        )
