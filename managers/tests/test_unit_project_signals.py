from django.test import TestCase
from django.utils import timezone

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
