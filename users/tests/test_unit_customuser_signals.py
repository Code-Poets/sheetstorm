from django.test import TestCase
from django.utils import timezone
from rest_framework.reverse import reverse

from managers.models import Project
from users.models import CustomUser


class TestCustomUserSignals(TestCase):

    def setUp(self):
        self.user = CustomUser(
            email="testuser@codepoets.it",
            password='newuserpasswd',
            user_type=CustomUser.UserType.MANAGER.name
        )
        self.user.full_clean()
        self.user.save()
        self.project = Project(
            name="TEST",
            start_date=timezone.now(),
        )
        self.project.save()
        self.project.managers.add(self.user)

    def test_user_should_not_be_in_project_as_manager_when_he_is_no_longer_manager(self):
        self.client.post(
            path=reverse('custom-user-update-by-admin', args=(self.user.pk,)),
            data={
                "email": "testuser@codepoets.it",
                "password": 'newuserpasswd',
                "user_type": CustomUser.UserType.EMPLOYEE.name
            },
        )
        self.user.refresh_from_db()
        self.assertEqual(self.user.user_type, CustomUser.UserType.EMPLOYEE.name)
        self.assertFalse(self.project in self.user.manager_projects.all())

