import datetime
from decimal import Decimal

from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory

from employees.models import Report
from employees.views import ReportViewSet
from managers.models import Project
from users.models import CustomUser


class ReportViewSetTests(TestCase):
    def setUp(self):
        self.user = CustomUser(
            email="testuser@example.com",
            password='newuserpasswd',
            first_name='John',
            last_name='Doe',
            country='PL'
        )
        self.user.full_clean()
        self.user.save()

        self.project = Project(
            name="Test Project",
            start_date=datetime.datetime.now(),
        )
        self.project.full_clean()
        self.project.save()

        self.report = Report(
            date=datetime.datetime.now().date(),
            description='Some description',
            author=self.user,
            project=self.project,
            work_hours=Decimal('8.00'),
        )
        self.report.full_clean()
        self.report.save()

    """
    -----------
    REPORT LIST
    -----------
    """
    def test_report_list_view_should_display_users_report_list(self):
        request = APIRequestFactory().get(path=reverse('report-list'))
        request.user = self.user
        response = ReportViewSet.as_view({'get': 'list'})(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.report.description)

    def test_report_list_view_should_not_be_accessible_for_unauthenticated_user(self):
        request = APIRequestFactory().get(path=reverse('report-list'))
        request.user = AnonymousUser()
        response = ReportViewSet.as_view({'get': 'list'})(request)
        self.assertEqual(response.status_code, 403)

    def test_report_list_view_should_not_display_other_users_reports(self):
        other_user=CustomUser(
            email="otheruser@example.com",
            password='otheruserpasswd',
            first_name='Jane',
            last_name='Doe',
            country='PL',
        )
        other_user.full_clean()
        other_user.save()

        other_report = Report(
            date=datetime.datetime.now().date(),
            description='Some other description',
            author=other_user,
            project=self.project,
            work_hours=Decimal('8.00'),
        )
        other_report.full_clean()
        other_report.save()

        request = APIRequestFactory().get(path=reverse('report-list'))
        request.user = self.user
        response = ReportViewSet.as_view({'get': 'list'})(request)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, other_report.description)

    def test_that_report_list_view_should_add_new_report_on_post(self):
        request = APIRequestFactory().post(
            path=reverse('report-list'),
            data={
                'date': datetime.datetime.now().date(),
                'description': 'Some description',
                'project': self.project,
                'work_hours': Decimal('8.00'),
            }
        )
        request.user = self.user
        response = ReportViewSet.as_view({'post': 'create'})(request)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Report.objects.all().count(), 2)

    """
    -------------
    REPORT DETAIL
    -------------
    """
    def test_report_detail_view_should_display_report_details(self):
        request = APIRequestFactory().get(path=reverse('report-detail', args=(self.report.pk,)))
        request.user = self.user
        response = ReportViewSet.as_view({'get': 'retrieve'})(request, pk=self.report.pk)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.report.description)

    def test_report_list_view_should_not_be_accessible_for_unauthenticated_users(self):
        request = APIRequestFactory().get(path=reverse('report-detail', args=(self.report.pk,)))
        request.user = AnonymousUser()
        response = ReportViewSet.as_view({'get': 'retrieve'})(request, pk=self.report.pk)
        self.assertEqual(response.status_code, 403)

    def test_report_detail_view_should_not_render_non_existing_report(self):
        request = APIRequestFactory().get(path=reverse('report-detail', args=(999,)))
        request.user = self.user
        response = ReportViewSet.as_view({'get': 'retrieve'})(request, pk=999)
        self.assertEqual(response.status_code, 404)

    def test_report_detail_view_should_update_report_on_put(self):
        new_description = 'Some other description'
        request = APIRequestFactory().put(
            path=reverse('report-detail', args=(self.report.pk,)),
            data={
                'date': datetime.datetime.now().date(),
                'description': new_description,
                'project': self.project,
                'work_hours': Decimal('8.00'),
            }
        )
        request.user = self.user
        response = ReportViewSet.as_view({'put': 'update'})(request, pk=self.report.pk)
        current_description = Report.objects.get(pk=self.report.pk).description
        self.assertEqual(response.status_code, 200)
        self.assertEqual(current_description, new_description)

    def test_report_detail_view_should_delete_report_on_delete(self):
        request = APIRequestFactory().delete(path=reverse('report-detail', args=(self.report.pk,)))
        request.user = self.user
        response = ReportViewSet.as_view({'delete': 'destroy'})(request, pk=self.report.pk)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Report.objects.all().count(), 0)
