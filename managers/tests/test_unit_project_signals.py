from django.test import TestCase
from django.utils import timezone
from freezegun import freeze_time

from employees.factories import TaskActivityTypeFactory
from employees.models import TaskActivityType
from managers.factories import ProjectFactory
from managers.models import Project
from users.models import CustomUser


class TestProjectSignals(TestCase):
    def setUp(self):
        self.employee = CustomUser(
            email="employee@codepoets.it", password="newuserpasswd", user_type=CustomUser.UserType.EMPLOYEE.name
        )
        self.employee.full_clean()
        self.employee.save()
        self.manager = CustomUser(
            email="manager@codepoets.it", password="newuserpasswd", user_type=CustomUser.UserType.MANAGER.name
        )
        self.manager.full_clean()
        self.manager.save()
        self.admin = CustomUser(
            email="admin@codepoets.it", password="adminpasswd", user_type=CustomUser.UserType.ADMIN.name
        )
        self.admin.full_clean()
        self.admin.save()
        self.project = Project(name="Test Project", start_date=timezone.now())
        self.project.full_clean()
        self.project.save()
        self.project.managers.add(self.manager)

    def test_user_should_be_updated_to_manager_when_he_is_assigned_as_a_project_manager(self):
        self.project.managers.add(self.employee)
        self.client.post(path="/admin/managers/project/add/", args=self.project)
        self.employee.refresh_from_db()
        self.assertEqual(self.employee.user_type, CustomUser.UserType.MANAGER.name)

    def test_user_should_be_updated_to_employee_when_he_is_no_longer_manager_of_any_project(self):
        self.project.managers.remove(self.manager)
        self.client.post(path=f"/admin/managers/project/{self.project.pk}/change/", args=self.project)
        self.manager.refresh_from_db()
        self.assertEqual(self.manager.user_type, CustomUser.UserType.EMPLOYEE.name)

    def test_admin_should_not_be_updated_to_manager_when_he_is_assigne_as_a_project_manager(self):
        self.project.managers.add(self.admin)
        self.client.post(path="/admin/managers/project/add/", args=self.project)
        self.admin.refresh_from_db()
        self.assertEqual(self.admin.user_type, CustomUser.UserType.ADMIN.name)

    def test_admin_should_not_be_updated_to_employee_when_he_is_no_longer_manager_of_any_project(self):
        self.project.managers.remove(self.admin)
        self.client.post(path=f"/admin/managers/project/{self.project.pk}/change/", args=self.project)
        self.admin.refresh_from_db()
        self.assertEqual(self.admin.user_type, CustomUser.UserType.ADMIN.name)

    def test_project_should_contain_default_task_activities_when_it_has_been_created(self):
        TaskActivityTypeFactory(is_default=True)
        not_default_task_activity = TaskActivityTypeFactory()
        project = ProjectFactory()
        list_of_project_activities = list(project.project_activities.all())

        self.assertEqual(list_of_project_activities, list(TaskActivityType.objects.get_defaults()))
        self.assertNotIn(not_default_task_activity, list_of_project_activities)

    def test_project_should_contain_default_and_custom_task_activities_after_update(self):
        default_task_activity = TaskActivityTypeFactory(is_default=True)
        custom_task_activity = TaskActivityTypeFactory()
        project = ProjectFactory()
        project.project_activities.add(custom_task_activity)
        project.refresh_from_db()

        self.assertCountEqual([custom_task_activity, default_task_activity], list(project.project_activities.all()))

    @freeze_time("2019-08-08")
    def test_project_should_not_be_suspended_when_project_is_completed(self):
        date = timezone.now().date() - timezone.timedelta(days=1)
        self.project.suspended = True
        self.project.stop_date = date
        self.project.save()
        self.project.refresh_from_db()

        self.assertEqual(self.project.suspended, False)
        self.assertEqual(self.project.stop_date, date)

    @freeze_time("2019-08-08")
    def test_project_could_be_suspended_when_stop_date_is_null(self):
        self.project.suspended = True
        self.project.save()
        self.project.refresh_from_db()

        self.assertEqual(self.project.suspended, True)
        self.assertEqual(self.project.stop_date, None)
