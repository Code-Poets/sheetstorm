from rest_framework.reverse import reverse

from managers import views
from managers.tests.test_api import ProjectTest


class ProjectUpdateViewTestCase(ProjectTest):
    def setUp(self):
        super().setUp()
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
        self.assertTemplateUsed(response, views.ProjectUpdateView.template_name)

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
