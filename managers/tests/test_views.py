from django.shortcuts import reverse
from django.test import TestCase
from django.utils import timezone
from parameterized import parameterized

from employees.factories import TaskActivityTypeFactory
from employees.models import TaskActivityType
from managers.factories import ProjectFactory
from managers.models import Project
from managers.views import ProjectCreateView
from managers.views import ProjectDetailView
from managers.views import ProjectsListView
from managers.views import ProjectUpdateView
from users.factories import AdminUserFactory
from users.factories import ManagerUserFactory
from users.factories import UserFactory
from users.models import CustomUser


class ProjectBaseTests(TestCase):
    def setUp(self):
        super().setUp()
        self.user = CustomUser(
            email="testuser@codepoets.it",
            first_name="John",
            last_name="Doe",
            user_type=CustomUser.UserType.ADMIN.name,
            is_active=True,
        )
        self.user.set_password("newuserpasswd")
        self.user.full_clean()
        self.user.save()
        self.client.force_login(self.user)


class ProjectDetailViewTests(ProjectBaseTests):
    def setUp(self):
        super().setUp()
        self.project = ProjectFactory()
        self.url = reverse("custom-project-detail", kwargs={"pk": self.project.pk})

    def test_project_detail_view_should_display_project_details_on_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.project.name)
        self.assertTemplateUsed(response, ProjectDetailView.template_name)


class ProjectsListViewTests(ProjectBaseTests):
    def setUp(self):
        super().setUp()
        self.project = ProjectFactory()
        self.url = reverse("custom-projects-list")

    def test_projects_list_view_for_admin_should_show_all_projects(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.project.name)
        self.assertTemplateUsed(response, ProjectsListView.template_name)

    def test_projects_list_view_for_manager_should_show_only_projects_in_which_he_is_manager(self):
        manager_user = UserFactory(user_type=CustomUser.UserType.MANAGER.name)
        manager_project = ProjectFactory()
        manager_project.managers.add(manager_user)
        self.client.force_login(manager_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, manager_project.name)
        self.assertNotContains(response, self.project.name)

    def test_projects_list_view_should_not_be_accessible_by_employee(self):
        employee_user = UserFactory(user_type=CustomUser.UserType.EMPLOYEE.name)
        self.client.force_login(employee_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("login") + f"?next={self.url}")


class ProjectsListOrderingViewTests(ProjectBaseTests):
    def setUp(self):
        super().setUp()
        self.project_1 = ProjectFactory(
            name="aaa",
            start_date=timezone.now() + timezone.timedelta(days=1),
            stop_date=timezone.now() + timezone.timedelta(days=6),
        )
        self.project_2 = ProjectFactory(
            name="abc",
            start_date=timezone.now() + timezone.timedelta(days=2),
            stop_date=timezone.now() + timezone.timedelta(days=5),
        )
        self.project_3 = ProjectFactory(
            name="cca",
            start_date=timezone.now() + timezone.timedelta(days=3),
            stop_date=timezone.now() + timezone.timedelta(days=4),
        )
        self.project_1.members.add(UserFactory())
        self.project_2.members.add(UserFactory(), UserFactory(), UserFactory())
        self.project_3.members.add(UserFactory(), UserFactory())
        self.url = reverse("custom-projects-list")

    def test_project_list_view_should_display_projects_sorted_by_name_ascending(self):
        response = self.client.get(self.url + "?sort=name")
        self.assertEqual(list(response.context_data["object_list"]), [self.project_1, self.project_2, self.project_3])

    def test_project_list_view_should_display_projects_sorted_by_name_descending(self):
        response = self.client.get(self.url + "?sort=-name")
        self.assertEqual(list(response.context_data["object_list"]), [self.project_3, self.project_2, self.project_1])

    def test_project_list_view_should_display_projects_sorted_by_start_date_ascending(self):
        response = self.client.get(self.url + "?sort=start_date")
        self.assertEqual(list(response.context_data["object_list"]), [self.project_1, self.project_2, self.project_3])

    def test_project_list_view_should_display_projects_sorted_by_start_date_descending(self):
        response = self.client.get(self.url + "?sort=-start_date")
        self.assertEqual(list(response.context_data["object_list"]), [self.project_3, self.project_2, self.project_1])

    def test_project_list_view_should_display_projects_sorted_by_stop_date_ascending(self):
        response = self.client.get(self.url + "?sort=stop_date")
        self.assertEqual(list(response.context_data["object_list"]), [self.project_3, self.project_2, self.project_1])

    def test_project_list_view_should_display_projects_sorted_by_stop_date_descending(self):
        response = self.client.get(self.url + "?sort=-stop_date")
        self.assertEqual(list(response.context_data["object_list"]), [self.project_1, self.project_2, self.project_3])

    def test_project_list_view_should_display_projects_sorted_by_members_count_ascending(self):
        response = self.client.get(self.url + "?sort=members_count")
        self.assertEqual(list(response.context_data["object_list"]), [self.project_1, self.project_3, self.project_2])

    def test_project_list_view_should_display_projects_sorted_by_members_count_descending(self):
        response = self.client.get(self.url + "?sort=-members_count")
        self.assertEqual(list(response.context_data["object_list"]), [self.project_2, self.project_3, self.project_1])


class ProjectCreateViewTests(ProjectBaseTests):
    def setUp(self):
        super().setUp()
        self.url = reverse("custom-project-create")
        self.data = {
            "name": "Another Example Project",
            "start_date": timezone.now().date() - timezone.timedelta(days=30),
            "suspended": False,
            "members": [self.user.pk],
        }

    def test_project_create_view_should_display_create_project_form_on_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, ProjectCreateView.template_name)

    def test_project_create_view_should_add_new_project_on_post_and_add_user_of_request_to_managers(self):
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Project.objects.count(), 1)
        project = Project.objects.get(name=self.data["name"])
        self.assertEqual(project.name, self.data["name"])
        self.assertEqual(project.start_date, self.data["start_date"])
        self.assertCountEqual([members.pk for members in project.members.all()], self.data["members"])
        self.assertEqual(project.suspended, self.data["suspended"])
        self.assertIn(self.user, project.managers.all())

    def test_project_create_view_should_not_add_new_project_on_post_if_data_is_invalid(self):
        del self.data["name"]
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, "form", "name", "This field is required.")
        self.assertEqual(Project.objects.count(), 0)


class ProjectUpdateViewTestCase(ProjectBaseTests):
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
        self.assertEqual(response.status_code, 404)
        self.project.refresh_from_db()
        self.assertEqual(self.project.managers.count(), 0)

    def test_project_update_view_should_display_all_aggregated_managers_on_get(self):
        self.project.managers.add(self.user)
        other_manager = ManagerUserFactory()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.user, response.context_data["form"].initial["managers"])
        self.assertNotIn(other_manager, response.context_data["form"].initial["managers"])
        self.assertContains(response, self.user)
        self.assertContains(response, other_manager)


class ProjectDeleteViewTests(ProjectBaseTests):
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


class ManageTaskActivitiesInProjectViewTests(TestCase):
    def setUp(self):
        super().setUp()
        self.user_admin = AdminUserFactory()
        self.client.force_login(self.user_admin)
        self.default_task_activity_1 = TaskActivityTypeFactory(is_default=True)
        self.default_task_activity_2 = TaskActivityTypeFactory(is_default=True)
        self.not_default_task_activity = TaskActivityTypeFactory()

        self.project = ProjectFactory()
        self.url = reverse("project-task-activities", kwargs={"pk": self.project.pk})

    def test_manage_task_activities_in_project_view_should_raise_404_for_manager_not_of_current_project(self):
        other_manager = ManagerUserFactory()
        self.client.force_login(other_manager)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 404)

    def test_manage_task_activities_in_project_view_should_get_200_when_user_is_manager_of_current_project(self):
        project_manager = ManagerUserFactory()
        self.project.managers.add(project_manager)
        self.client.force_login(project_manager)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_manage_task_activities_in_project_view_should_redirect_on_employee_get(self):
        user_employee = UserFactory()
        self.project.members.add(user_employee)
        self.client.force_login(user_employee)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)

    def test_manage_task_activities_view_should_show_all_task_activities_in_project_and_available_to_add(self):
        self.assertCountEqual(self.project.project_activities.all(), TaskActivityType.objects.get_defaults())
        self.assertNotIn(self.not_default_task_activity, self.project.project_activities.all())

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.default_task_activity_1.name)
        self.assertContains(response, self.not_default_task_activity.name)

    def test_manage_task_activities_view_should_add_new_task_activity_on_post_and_add_it_to_project(self):
        task_activity_name = "New activity"
        response = self.client.post(self.url, data={"name": task_activity_name})

        self.assertEqual(response.status_code, 302)
        self.assertIn(TaskActivityType.objects.get(name=task_activity_name), self.project.project_activities.all())

    def test_manage_task_activities_view_should_add_existing_task_activity_to_project_on_add_to_project_function(self):
        number_of_all_task_activities_before_add = self.project.project_activities.all().count()

        response = self.client.post(self.url, data={"task_activities": self.not_default_task_activity.pk})
        number_of_all_task_activities_after_add_one_new_task_activity = self.project.project_activities.all().count()
        num_of_added_task_activities = 1

        self.assertEqual(response.status_code, 302)
        self.assertIn(self.not_default_task_activity, self.project.project_activities.all())
        self.assertEqual(
            number_of_all_task_activities_after_add_one_new_task_activity,
            number_of_all_task_activities_before_add + num_of_added_task_activities,
        )


class RemoveTaskActivityFromProjectViewTests(TestCase):
    def setUp(self):
        super().setUp()
        self.user_admin = AdminUserFactory()
        self.client.force_login(self.user_admin)
        self.default_task_activity = TaskActivityTypeFactory(is_default=True)

        self.project = ProjectFactory()
        self.url = reverse(
            "remove-task-activity-from-project",
            kwargs={"pk": self.project.pk, "task_activity_pk": self.default_task_activity.pk},
        )

    def test_remove_task_activities_view_should_remove_task_activity_from_relation_on_delete_from_project_function(
        self
    ):
        number_of_project_task_activities_before_remove = self.project.project_activities.all().count()
        self.assertIn(self.default_task_activity, self.project.project_activities.all())

        response = self.client.post(self.url)
        number_of_project_task_activities_after_remove = self.project.project_activities.all().count()
        removed_task_activities = 1

        self.project.project_activities.all().count()
        self.assertEqual(response.status_code, 302)

        self.assertNotIn(self.default_task_activity, self.project.project_activities.all())
        self.assertEqual(
            number_of_project_task_activities_after_remove,
            number_of_project_task_activities_before_remove - removed_task_activities,
        )

    def test_remove_task_activities_view_should_only_handle_post(self):
        post_response = self.client.post(self.url, data={"task_activity_pk": self.default_task_activity.pk})
        self.assertEqual(post_response.status_code, 302)

        get_response = self.client.get(self.url, data={"task_activity_pk": self.default_task_activity.pk})
        self.assertEqual(get_response.status_code, 405)

    def test_manage_task_activities_view_should_raise_404_when_user_is_not_manager_of_current_project(self):
        manager = ManagerUserFactory()
        self.client.force_login(manager)

        response = self.client.post(self.url, data={"task_activity_pk": self.default_task_activity.pk})

        self.assertEqual(response.status_code, 404)
