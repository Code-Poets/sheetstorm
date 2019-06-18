from django.test import RequestFactory
from django.test import TestCase
from django.views.generic import ListView

from employees.factories import ReportFactory
from employees.models import Report
from managers.factories import ProjectFactory
from managers.models import Project
from users.factories import UserFactory
from users.models import CustomUser
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

    def test_that_user_is_author_of_current_report_mixin_should_limit_view_report_queryset_if_user_is_employee(self):
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

    def test_that_user_is_author_of_current_report_mixin_should_not_limit_view_report_queryset_if_user_is_not_employee(
        self
    ):
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

    def test_that_user_is_manager_of_current_project_mixin_should_limit_view_project_queryset_if_user_is_manager(self):
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

    def test_that_user_is_manager_of_current_project_mixin_should_not_limit_view_project_queryset_if_user_is_not_manager(
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

    def test_that_user_is_manager_of_current_project_or_author_of_current_report_mixin_should_limit_view_project_queryset_if_user_is_manager(
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

    def test_that_user_is_manager_of_current_project_or_author_of_current_report_mixin_should_not_limit_view_project_queryset_if_user_is_not_manager(
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
