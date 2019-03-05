from rest_framework.reverse import reverse
from django.shortcuts import reverse

from django.test import TestCase

from managers.factories import ProjectFactory
from users.models import CustomUser


class ProjectsListTests(TestCase):

    def setUp(self):
        self.url = reverse('project-list')
        self.user = CustomUser.objects._create_user(
            "testuser@codepoets.it",
            "testuserpasswd",
            False,
            False,
            CustomUser.UserType.MANAGER.name,
        )

    def test_project_list_view_should_display_project_list_ordered_by_name(self):
        project_1 = ProjectFactory(name='Bc')
        project_2 = ProjectFactory(name='Zx')
        project_3 = ProjectFactory(name='Ab')

        expected_project_order = [
            project_3.name, project_1.name, project_2.name
        ]

        self.client.force_login(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [project['name'] for project in response.data],
            expected_project_order,
        )

    def test_project_list_view_should_display_project_list_ordered_by_name_case_insensitive(self):
        project_1 = ProjectFactory(name='Bc')
        project_2 = ProjectFactory(name='Zx')
        project_3 = ProjectFactory(name='ab')

        expected_project_order = [
            project_3.name, project_1.name, project_2.name
        ]

        self.client.force_login(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [project['name'] for project in response.data],
            expected_project_order,
        )

    def test_project_list_view_should_display_project_list_ordered_by_name_regardless_case(self):
        project_1 = ProjectFactory(name='Bc')
        project_2 = ProjectFactory(name='Az')
        project_3 = ProjectFactory(name='ab')

        expected_project_order = [
            project_3.name, project_2.name, project_1.name
        ]

        self.client.force_login(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [project['name'] for project in response.data],
            expected_project_order,
        )
