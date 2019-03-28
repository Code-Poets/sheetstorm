import datetime
from decimal import Decimal

from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory

from employees.models import Report
from employees.views import delete_report
from employees.views import ReportDetail
from employees.views import ReportList
from employees.views import ReportViewSet
from managers.models import Project
from users.models import CustomUser


class ReportViewSetTests(TestCase):
    def setUp(self):
        self.user = CustomUser(
            email="testuser@codepoets.it",
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
    def test_report_list_view_should_display_users_report_list_on_get(self):
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
        other_user = CustomUser(
            email="otheruser@codepoets.it",
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

    def test_report_list_view_should_add_new_report_on_post(self):
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
    def test_report_detail_view_should_display_report_details_on_get(self):
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

    def test_report_detail_view_should_not_render_non_existing_report_on_get(self):
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


class ReportListTests(TestCase):
    def setUp(self):
        self.user = CustomUser(
            email="testuser@codepoets.it",
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
        self.url = reverse('custom-report-list')

    def test_custom_list_view_should_display_users_report_list_on_get(self):
        request = APIRequestFactory().get(path=self.url)
        request.user = self.user
        response = ReportList.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.report.description)
        dictionary = response.data['reports_dict']
        reports = list(dictionary.values())[0]
        self.assertTrue(self.report in reports)

    def test_custom_list_view_should_not_be_accessible_for_unauthenticated_user(self):
        request = APIRequestFactory().get(path=self.url)
        request.user = AnonymousUser()
        response = ReportList.as_view()(request)
        self.assertEqual(response.status_code, 403)

    def test_custom_list_view_should_not_display_other_users_reports(self):
        other_user = CustomUser(
            email="otheruser@codepoets.it",
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

        request = APIRequestFactory().get(path=self.url)
        request.user = self.user
        response = ReportList.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, other_report.description)

    def test_custom_report_list_view_should_add_new_report_on_post(self):
        request = APIRequestFactory().post(
            path=self.url,
            data={
                'date': datetime.datetime.now().date(),
                'description': 'Some description',
                'project': self.project,
                'work_hours': Decimal('8.00'),
            }
        )
        request.user = self.user
        response = ReportList.as_view()(request)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Report.objects.all().count(), 2)

    def test_custom_report_list_view_should_not_add_new_report_on_post_if_form_is_invalid(self):
        request = APIRequestFactory().post(
            path=self.url,
            data={
                'description': 'Some description',
                'project': self.project,
                'work_hours': Decimal('8.00'),
            }
        )
        request.user = self.user
        response = ReportList.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Report.objects.all().count(), 1)
        self.assertIsNotNone(response.data['errors'])

    def test_get_queryset_method_should_return_queryset_containing_all_of_current_users_reports(self):
        other_user = CustomUser(
            email="otheruser@codepoets.it",
            password='otheruserpasswd',
            first_name='Jane',
            last_name='Doe',
            country='PL',
        )
        other_user.full_clean()
        other_user.save()

        other_project = Project(
            name="Project test",
            start_date=datetime.datetime.now(),
        )
        other_project.full_clean()
        other_project.save()

        other_user_report = Report(
            date=datetime.datetime.now().date(),
            description='Some other description',
            author=other_user,
            project=self.project,
            work_hours=Decimal('8.00'),
        )
        other_user_report.full_clean()
        other_user_report.save()

        other_report_1 = Report(
            date=datetime.datetime.now().date(),
            description='Some other description',
            author=self.user,
            project=other_project,
            work_hours=Decimal('8.00'),
        )
        other_report_1.full_clean()
        other_report_1.save()

        other_report_2 = Report(
            date=datetime.date(2001, 1, 1),
            description='Some other description',
            author=self.user,
            project=self.project,
            work_hours=Decimal('8.00'),
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


class ReportDetailTests(TestCase):
    def setUp(self):
        self.user = CustomUser(
            email="testuser@codepoets.it",
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

    def test_custom_report_detail_view_should_display_report_details_on_get(self):
        request = APIRequestFactory().get(path=reverse('custom-report-detail', args=(self.report.pk,)))
        request.user = self.user
        response = ReportDetail.as_view()(request, pk=self.report.pk)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.report.description)
        self.assertEqual(response.data['serializer'].instance, self.report)

    def test_custom_report_list_view_should_not_be_accessible_for_unauthenticated_users(self):
        request = APIRequestFactory().get(path=reverse('custom-report-detail', args=(self.report.pk,)))
        request.user = AnonymousUser()
        response = ReportDetail.as_view()(request, pk=self.report.pk)
        self.assertEqual(response.status_code, 403)

    def test_custom_report_detail_view_should_not_render_non_existing_report(self):
        request = APIRequestFactory().get(path=reverse('custom-report-detail', args=(999,)))
        request.user = self.user
        response = ReportDetail.as_view()(request, pk=999)
        self.assertEqual(response.status_code, 404)

    def test_custom_report_detail_view_should_update_report_on_post(self):
        new_description = 'Some other description'
        request = APIRequestFactory().post(
            path=reverse('custom-report-detail', args=(self.report.pk,)),
            data={
                'date': datetime.datetime.now().date(),
                'description': new_description,
                'project': self.project,
                'work_hours': Decimal('8.00'),
            },
        )
        request.user = self.user
        response = ReportDetail.as_view()(request, pk=self.report.pk)
        self.report.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.report.description, new_description)

    def test_custom_report_detail_view_should_not_update_report_on_discard(self):
        new_description = 'Some other description'
        request = APIRequestFactory().post(
            path=reverse('custom-report-detail', args=(self.report.pk,)),
            data={
                'date': datetime.datetime.now().date(),
                'description': new_description,
                'project': self.project,
                'work_hours': Decimal('8.00'),
                'discard': "Discard"
            },
        )
        request.user = self.user
        response = ReportDetail.as_view()(request, pk=self.report.pk)
        self.report.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertNotEqual(self.report.description, new_description)

    def test_custom_report_detail_view_should_not_update_report_on_post_if_form_is_invalid(self):
        new_description = 'Some other description'
        request = APIRequestFactory().post(
            path=reverse('custom-report-detail', args=(self.report.pk,)),
            data={
                'description': new_description,
                'project': self.project,
                'work_hours': Decimal('8.00'),
            },
        )
        request.user = self.user
        response = ReportDetail.as_view()(request, pk=self.report.pk)
        self.report.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data['errors'])
        self.assertNotEqual(new_description, self.report.description)


class DeleteReportTests(TestCase):
    def setUp(self):
        self.user = CustomUser(
            email="testuser@codepoets.it",
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

    def test_delete_report_view_should_delete_report_on_post(self):
        request = APIRequestFactory().delete(path=reverse('custom-report-delete', args=(self.report.pk,)))
        request.user = self.user
        response = delete_report(request, pk=self.report.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Report.objects.all().count(), 0)
