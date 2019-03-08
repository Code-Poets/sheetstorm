import datetime

from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory

from managers import views
from managers.factories import ProjectFactory
from managers.models import Project
from users.models import CustomUser


class ProjectsListTests(TestCase):
    def setUp(self):
        self.url = reverse("project-list")
        self.user = CustomUser.objects._create_user(
            "testuser@codepoets.it", "testuserpasswd", False, False, CustomUser.UserType.MANAGER.name
        )

    def test_project_list_view_should_display_project_list_ordered_by_name(self):
        project_1 = ProjectFactory(name="Bc")
        project_2 = ProjectFactory(name="Zx")
        project_3 = ProjectFactory(name="Ab")

        expected_project_order = [project_3.name, project_1.name, project_2.name]

        self.client.force_login(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual([project["name"] for project in response.data], expected_project_order)

    def test_project_list_view_should_display_project_list_ordered_by_name_case_insensitive(self):
        project_1 = ProjectFactory(name="Bc")
        project_2 = ProjectFactory(name="Zx")
        project_3 = ProjectFactory(name="ab")

        expected_project_order = [project_3.name, project_1.name, project_2.name]

        self.client.force_login(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual([project["name"] for project in response.data], expected_project_order)

    def test_project_list_view_should_display_project_list_ordered_by_name_regardless_case(self):
        project_1 = ProjectFactory(name="Bc")
        project_2 = ProjectFactory(name="Az")
        project_3 = ProjectFactory(name="ab")

        expected_project_order = [project_3.name, project_2.name, project_1.name]

        self.client.force_login(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual([project["name"] for project in response.data], expected_project_order)


class ProjectTest(TestCase):
    def setUp(self):
        super().setUp()
        self.user = CustomUser(
            email="testuser@codepoets.it",
            first_name="John",
            last_name="Doe",
            country="PL",
            user_type=CustomUser.UserType.ADMIN.name,
        )
        self.user.set_password("newuserpasswd")
        self.user.full_clean()
        self.user.save()
        self.client.force_login(self.user)

        self.project = Project(
            name="Example Project",
            start_date=datetime.datetime.now().date() - datetime.timedelta(days=30),
            stop_date=datetime.datetime.now().date(),
            terminated=False,
        )
        self.project.full_clean()
        self.project.save()
        self.project.managers.add(self.user)
        self.project.members.add(self.user)


class CustomProjectsListTests(ProjectTest):
    def setUp(self):
        super().setUp()
        self.url = reverse("custom-projects-list")

    def test_project_list_view_should_display_projects_list_on_get(self):
        request = APIRequestFactory().get(path=self.url)
        request.user = self.user
        response = views.ProjectsList.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.project.name)
        projects_list = response.context_data["object_list"]
        self.assertTrue(self.project in projects_list)

    def test_projects_list_view_should_show_for_managers_only_own_projects(self):
        self.user.user_type = CustomUser.UserType.MANAGER.name
        manager_project_list = Project.objects.filter(managers__id=self.user.pk)
        request = APIRequestFactory().get(path=self.url)
        request.user = self.user
        response = views.ProjectsList.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.project.name)
        projects_list = response.context_data["object_list"]
        self.assertEqual(list(manager_project_list), list(projects_list))

    def test_project_list_view_should_display_projects_sorted_by_name_ascending(self):
        request = APIRequestFactory().get(path=self.url + "?sort=name")
        request.user = self.user
        response = views.ProjectsList.as_view()(request)
        projects_list = response.context_data["object_list"]
        self.assertTrue(projects_list.ordered)
        self.assertTrue("name" in projects_list.query.order_by)

    def test_project_list_view_should_display_projects_sorted_by_name_descending(self):
        request = APIRequestFactory().get(path=self.url + "?sort=-name")
        request.user = self.user
        response = views.ProjectsList.as_view()(request)
        projects_list = response.context_data["object_list"]
        self.assertTrue(projects_list.ordered)
        self.assertTrue("-name" in projects_list.query.order_by)

    def test_project_list_view_should_display_projects_sorted_by_start_date_ascending(self):
        request = APIRequestFactory().get(path=self.url + "?sort=start_date")
        request.user = self.user
        response = views.ProjectsList.as_view()(request)
        projects_list = response.context_data["object_list"]
        self.assertTrue(projects_list.ordered)
        self.assertTrue("start_date" in projects_list.query.order_by)

    def test_project_list_view_should_display_projects_sorted_by_start_date_descending(self):
        request = APIRequestFactory().get(path=self.url + "?sort=-start_date")
        request.user = self.user
        response = views.ProjectsList.as_view()(request)
        projects_list = response.context_data["object_list"]
        self.assertTrue(projects_list.ordered)
        self.assertTrue("-start_date" in projects_list.query.order_by)

    def test_project_list_view_should_display_projects_sorted_by_stop_date_ascending(self):
        request = APIRequestFactory().get(path=self.url + "?sort=stop_date")
        request.user = self.user
        response = views.ProjectsList.as_view()(request)
        projects_list = response.context_data["object_list"]
        self.assertTrue(projects_list.ordered)
        self.assertTrue("stop_date" in projects_list.query.order_by)

    def test_project_list_view_should_display_projects_sorted_by_stop_date_descending(self):
        request = APIRequestFactory().get(path=self.url + "?sort=-stop_date")
        request.user = self.user
        response = views.ProjectsList.as_view()(request)
        projects_list = response.context_data["object_list"]
        self.assertTrue(projects_list.ordered)
        self.assertTrue("-stop_date" in projects_list.query.order_by)

    def test_project_list_view_should_display_projects_sorted_by_members_count_ascending(self):
        request = APIRequestFactory().get(path=self.url + "?sort=members_count")
        request.user = self.user
        response = views.ProjectsList.as_view()(request)
        projects_list = response.context_data["object_list"]
        self.assertTrue(projects_list.ordered)
        self.assertTrue("members_count" in projects_list.query.order_by)

    def test_project_list_view_should_display_projects_sorted_by_members_count_descending(self):
        request = APIRequestFactory().get(path=self.url + "?sort=-members_count")
        request.user = self.user
        response = views.ProjectsList.as_view()(request)
        projects_list = response.context_data["object_list"]
        self.assertTrue(projects_list.ordered)
        self.assertTrue("-members_count" in projects_list.query.order_by)


class ProjectDetailTests(ProjectTest):
    def setUp(self):
        super().setUp()
        self.url = reverse("custom-project-detail", args=(self.project.pk,))

    def test_project_detail_view_should_display_project_details_on_get(self):
        request = APIRequestFactory().get(path=self.url)
        request.user = self.user
        response = views.ProjectDetail.as_view()(request, self.project.pk)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.project.name)
        project = response.data["project"]
        self.assertEqual(self.project, project)

    def test_project_detail_view_should_return_404_status_code_on_get_if_project_does_not_exist(self):
        request = APIRequestFactory().get(path=self.url)
        request.user = self.user
        response = views.ProjectDetail.as_view()(request, self.project.pk + 1)
        self.assertEqual(response.status_code, 404)


class ProjectCreateTests(ProjectTest):
    def setUp(self):
        super().setUp()
        self.url = reverse("custom-project-create", kwargs={"pk": self.project.pk})
        self.data = {
            'name': 'Another Example Project',
            'start_date': datetime.datetime.now().date() - datetime.timedelta(days=30),
            'terminated': False,
            'managers': [self.user.pk],
            'members': [self.user.pk],
        }

    def test_project_create_view_should_display_create_project_form_on_get(self):
        request = APIRequestFactory().get(path=self.custom_projects_list_url[3])
        request.user = self.user
        response = views.ProjectCreate.as_view()(request,)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create new project')

    def test_project_create_view_should_add_new_project_on_post(self):
        request = APIRequestFactory().post(
            path=self.custom_projects_list_url[3],
            data=self.data
        )
        request.user = self.user
        response = views.ProjectCreate.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/managers/projects/')
        self.assertEqual(Project.objects.filter(name='Another Example Project').count(), 1)

    def test_project_create_view_should_not_add_new_project_on_post_if_data_is_invalid(self):
        request = APIRequestFactory().post(
            path=self.custom_projects_list_url[3],
            data={
                'start_date': datetime.datetime.now().date() - datetime.timedelta(days=30),
                'terminated': False,
                'managers': [self.user.pk, ],
                'members': [self.user.pk, ],
            }
        )
        request.user = self.user
        response = views.ProjectCreate.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.data.get('errors'), None)
        self.assertTrue('name' in response.data.get('errors'))
        self.assertEqual(Project.objects.filter(name='Another Example Project').count(), 0)
