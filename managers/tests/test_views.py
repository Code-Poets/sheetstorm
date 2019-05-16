import datetime

from django.shortcuts import reverse
from parameterized import parameterized

from managers.factories import ProjectFactory
from managers.models import Project
from managers.tests.test_api import ProjectTest
from managers.views import ProjectCreateView
from managers.views import ProjectDetailView
from managers.views import ProjectUpdateView
from users.factories import UserFactory
from users.models import CustomUser


class ProjectDetailViewTests(ProjectTest):
    def setUp(self):
        super().setUp()
        self.project = ProjectFactory()
        self.url = reverse("custom-project-detail", kwargs={"pk": self.project.pk})

    def test_project_detail_view_should_display_project_details_on_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.project.name)
        self.assertTemplateUsed(response, ProjectDetailView.template_name)


class ProjectCreateViewTests(ProjectTest):
    def setUp(self):
        super().setUp()
        self.url = reverse("custom-project-create")
        self.data = {
            "name": "Another Example Project",
            "start_date": datetime.datetime.now().date() - datetime.timedelta(days=30),
            "terminated": False,
            "managers": [self.user.pk],
            "members": [self.user.pk],
        }

    def test_project_create_view_should_display_create_project_form_on_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, ProjectCreateView.template_name)

    def test_project_create_view_should_add_new_project_on_post(self):
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Project.objects.count(), 1)
        self.assertTrue(Project.objects.filter(name=self.data["name"]).exists())

    def test_project_create_view_should_not_add_new_project_on_post_if_data_is_invalid(self):
        del self.data["name"]
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, "form", "name", "This field is required.")
        self.assertEqual(Project.objects.count(), 0)


class ProjectUpdateViewTestCase(ProjectTest):
    def setUp(self):
        super().setUp()
        self.project = ProjectFactory()
        self.url = reverse("custom-project-update", kwargs={"pk": self.project.pk})
        self.data = {
            "name": "New Example Project Name",
            "start_date": self.project.start_date,
            "managers": [self.user.pk],
            "members": [self.user.pk],
        }

    def test_project_update_view_should_display_update_template(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.project.name)
        self.assertTemplateUsed(response, ProjectUpdateView.template_name)

    def test_project_update_view_should_return_404_status_code_on_get_if_project_does_not_exist(self):
        response = self.client.get(reverse("custom-project-update", kwargs={"pk": self.project.pk + 1}))
        self.assertEqual(response.status_code, 404)

    def test_project_update_view_should_update_project_on_post(self):
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 302)
        self.project.refresh_from_db()
        self.assertEqual(self.project.name, self.data["name"])

    def test_project_update_view_should_update_project_on_post_if_data_is_invalid(self):
        del self.data["name"]
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 200)
        self.project.refresh_from_db()
        self.assertFormError(response, "form", "name", "This field is required.")

    def test_project_update_view_should_not_update_managers_if_user_is_manager(self):
        assert self.project.managers.count() == 0
        user_manager = UserFactory(user_type=CustomUser.UserType.MANAGER.name)
        self.client.force_login(user=user_manager)
        self.data["managers"] = [self.user.pk, user_manager.pk]
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 302)
        self.project.refresh_from_db()
        self.assertEqual(self.project.managers.count(), 0)


class ProjectDeleteViewTests(ProjectTest):
    def setUp(self):
        super().setUp()
        self.project = ProjectFactory()
        self.url = reverse("custom-project-delete", kwargs={"pk": self.project.pk})

    def test_delete_project_function_view_should_delete_project_on_admin_type_user_post(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Project.objects.all().count(), 0)

    @parameterized.expand([(CustomUser.UserType.EMPLOYEE.name,), (CustomUser.UserType.MANAGER.name,)])
    def test_delete_project_function_view_should_not_delete_project_on_non_admin_request(self, user_type):
        self.user.user_type = user_type
        self.user.full_clean()
        self.user.save()
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Project.objects.all().count(), 1)
