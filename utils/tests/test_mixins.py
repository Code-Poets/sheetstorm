from django.test import RequestFactory
from django.test import TestCase
from django.utils import timezone
from django.views.generic import ListView
from freezegun import freeze_time
from mock import patch

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

        class TestView(ProjectsWorkPercentageMixin, ListView):
            model = Report

        self.view = TestView.as_view()
        self.request_factory = RequestFactory()
        self.request = self.request_factory.get("anything")
        self.request.user = UserFactory()

    def test_project_work_percentage_mixin_should_call_get_projects_work_percentage_with_none_parameters(self):
        with patch("users.models.CustomUser.get_projects_work_percentage") as get_projects_work_percentage:
            response = self.view(self.request)

        self.assertEqual(response.status_code, 200)
        get_projects_work_percentage.assert_called_once_with(None, None)

    def test_project_work_percentage_mixin_should_call_get_projects_work_percentage_with_parameters_if_provided_to_view(
        self
    ):
        with patch("users.models.CustomUser.get_projects_work_percentage") as get_projects_work_percentage:
            response = self.view(self.request, year=2000, month=11)

        self.assertEqual(response.status_code, 200)
        get_projects_work_percentage.assert_called_once_with(
            timezone.now().date().replace(year=2000, month=11, day=1),
            timezone.now().date().replace(year=2000, month=11, day=30),
        )

    def test_project_work_percentage_mixin_should_call_get_projects_work_percentage_with_last_30_days_paramemeters_if_current_month_and_year(
        self
    ):
        current_date = timezone.now().date()

        with patch("users.models.CustomUser.get_projects_work_percentage") as get_projects_work_percentage:
            response = self.view(self.request, year=current_date.year, month=current_date.month)

        self.assertEqual(response.status_code, 200)
        get_projects_work_percentage.assert_called_once_with(current_date - timezone.timedelta(days=30), current_date)
