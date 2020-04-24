from django.shortcuts import reverse
from django.test import TestCase
from django.utils import timezone

from managers.models import Project
from users.factories import AdminUserFactory
from users.factories import ManagerUserFactory
from users.models import CustomUser


class TestCustomUserSignals(TestCase):
    def setUp(self):
        self.user = ManagerUserFactory()
        self.user.full_clean()
        self.user.save()
        self.user_admin = AdminUserFactory()
        self.client.force_login(self.user_admin)
        self.project = Project(name="TEST", start_date=timezone.now())
        self.project.save()
        self.project.managers.add(self.user)
        self.project.members.add(self.user)

    def test_user_should_not_be_in_project_as_manager_when_he_is_no_longer_manager(self):
        response = self.client.post(
            path=reverse("custom-user-update-by-admin", args=(self.user.pk,)),
            data={
                "email": self.user.email,
                "password": self.user.password,
                "user_type": CustomUser.UserType.EMPLOYEE.name,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.user_type, CustomUser.UserType.EMPLOYEE.name)
        self.assertFalse(self.project in self.user.manager_projects.all())

    def test_user_should_not_be_a_project_member_when_he_is_no_longer_active(self):
        superuser = AdminUserFactory(is_staff=True, is_superuser=True)
        self.client.force_login(superuser)
        response = self.client.post(
            path=f"/admin/users/customuser/{self.user.pk}/change/",
            data={
                "email": self.user.email,
                "password": self.user.password,
                "user_type": self.user.user_type,
                "is_active": False,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.user_type, CustomUser.UserType.EMPLOYEE.name)
        self.assertFalse(self.project in self.user.projects.all())
