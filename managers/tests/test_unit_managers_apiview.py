import datetime

from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory

from django.test import TestCase

from managers import views
from managers.models import Project
from users.models import CustomUser


class ProjectTest(TestCase):
    def setUp(self):
        super().setUp()
        self.user = CustomUser(
            email='testuser@codepoets.it',
            first_name='John',
            last_name='Doe',
            country='PL',
            user_type=CustomUser.UserType.ADMIN.name,
        )
        self.user.set_password('newuserpasswd')
        self.user.full_clean()
        self.user.save()

        self.project = Project(
            name='Example Project',
            start_date=datetime.datetime.now().date() - datetime.timedelta(days=30),
            stop_date=datetime.datetime.now().date(),
            terminated=False,
        )
        self.project.full_clean()
        self.project.save()
        self.project.managers.add(self.user)
        self.project.members.add(self.user)
        self.custom_projects_list_url = [
            reverse('custom-projects-list'),
        ]


class ProjectsListTests(ProjectTest):
    def test_project_list_view_should_display_projects_list_on_get(self):
        request = APIRequestFactory().get(path=self.custom_projects_list_url[0])
        request.user = self.user
        response = views.ProjectsList.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.project.name)
        projects_list = response.context_data['object_list']
        self.assertTrue(self.project in projects_list)

    def test_projects_list_view_should_show_for_managers_only_own_projects(self):
        self.user.user_type = CustomUser.UserType.MANAGER.name
        manager_project_list = Project.objects.filter(managers__id=self.user.pk)
        request = APIRequestFactory().get(path=self.custom_projects_list_url[0])
        request.user = self.user
        response = views.ProjectsList.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.project.name)
        projects_list = response.context_data['object_list']
        self.assertEqual(list(manager_project_list), list(projects_list))

    def test_project_list_view_should_display_projects_sorted_by_name_ascending(self):
        request = APIRequestFactory().get(path=self.custom_projects_list_url[0] + '?sort=name')
        request.user = self.user
        response = views.ProjectsList.as_view()(request)
        projects_list = response.context_data['object_list']
        self.assertTrue(projects_list.ordered)
        self.assertTrue('name' in projects_list.query.order_by)

    def test_project_list_view_should_display_projects_sorted_by_name_descending(self):
        request = APIRequestFactory().get(path=self.custom_projects_list_url[0] + '?sort=-name')
        request.user = self.user
        response = views.ProjectsList.as_view()(request)
        projects_list = response.context_data['object_list']
        self.assertTrue(projects_list.ordered)
        self.assertTrue('-name' in projects_list.query.order_by)

    def test_project_list_view_should_display_projects_sorted_by_start_date_ascending(self):
        request = APIRequestFactory().get(path=self.custom_projects_list_url[0] + '?sort=start_date')
        request.user = self.user
        response = views.ProjectsList.as_view()(request)
        projects_list = response.context_data['object_list']
        self.assertTrue(projects_list.ordered)
        self.assertTrue('start_date' in projects_list.query.order_by)

    def test_project_list_view_should_display_projects_sorted_by_start_date_descending(self):
        request = APIRequestFactory().get(path=self.custom_projects_list_url[0] + '?sort=-start_date')
        request.user = self.user
        response = views.ProjectsList.as_view()(request)
        projects_list = response.context_data['object_list']
        self.assertTrue(projects_list.ordered)
        self.assertTrue('-start_date' in projects_list.query.order_by)

    def test_project_list_view_should_display_projects_sorted_by_stop_date_ascending(self):
        request = APIRequestFactory().get(path=self.custom_projects_list_url[0] + '?sort=stop_date')
        request.user = self.user
        response = views.ProjectsList.as_view()(request)
        projects_list = response.context_data['object_list']
        self.assertTrue(projects_list.ordered)
        self.assertTrue('stop_date' in projects_list.query.order_by)

    def test_project_list_view_should_display_projects_sorted_by_stop_date_descending(self):
        request = APIRequestFactory().get(path=self.custom_projects_list_url[0] + '?sort=-stop_date')
        request.user = self.user
        response = views.ProjectsList.as_view()(request)
        projects_list = response.context_data['object_list']
        self.assertTrue(projects_list.ordered)
        self.assertTrue('-stop_date' in projects_list.query.order_by)

    def test_project_list_view_should_display_projects_sorted_by_members_count_ascending(self):
        request = APIRequestFactory().get(path=self.custom_projects_list_url[0] + '?sort=members_count')
        request.user = self.user
        response = views.ProjectsList.as_view()(request)
        projects_list = response.context_data['object_list']
        self.assertTrue(projects_list.ordered)
        self.assertTrue('members_count' in projects_list.query.order_by)

    def test_project_list_view_should_display_projects_sorted_by_members_count_descending(self):
        request = APIRequestFactory().get(path=self.custom_projects_list_url[0] + '?sort=-members_count')
        request.user = self.user
        response = views.ProjectsList.as_view()(request)
        projects_list = response.context_data['object_list']
        self.assertTrue(projects_list.ordered)
        self.assertTrue('-members_count' in projects_list.query.order_by)
