from django_mock_queries.query import MockSet
from django.test import TestCase
from django.test import Client

from mock import patch
from mock import MagicMock
from model_mommy import mommy

from users import permissions
from users.common import constants
from users.models import CustomUser


class BaseHasPermissionsTestCase(TestCase):
    def create_user(self, user_type):
        password = 'password'
        user = mommy.prepare(
            CustomUser,
            user_type=user_type,
        )
        user.email = user.email.split('@')[0] + '@' + constants.VALID_EMAIL_DOMAIN_LIST[0]
        user.set_password(password)
        user.full_clean()
        user.save()
        return (user, password)

    def get_viewset_as(self,  url, user=None, password=None):
        api = Client()
        if user:
            api.login(email=user.email, password=password)
            return api.get(url)


class BaseHasObjectPermissionsTestCase(TestCase):
    object_owners = MockSet()

    def create_object_owner(self, user_type):
        self.request.user.user_type = user_type
        self.object_owners.add(
            MagicMock(user=self.request.user)
        )


class TestAuthenticatedAdminPermissions(BaseHasPermissionsTestCase):
    url = '/api/users/'

    def test_users_viewset_returns_200_for_admin_type_user(self):
        response = self.get_viewset_as(
            self.url,
            *self.create_user(CustomUser.UserType.ADMIN.name),
        )
        self.assertEqual(response.status_code, 200)

    def test_users_viewset_returns_403_for_manager_type_user(self):
        response = self.get_viewset_as(
            self.url,
            *self.create_user(CustomUser.UserType.MANAGER.name),
        )
        self.assertEqual(response.status_code, 403)

    def test_users_viewset_returns_403_for_employee_type_user(self):
        response = self.get_viewset_as(
            self.url,
            *self.create_user(CustomUser.UserType.EMPLOYEE.name),
        )
        self.assertEqual(response.status_code, 403)


class TestAuthenticatedAdminOrOwnerUserPermissions(BaseHasPermissionsTestCase, BaseHasObjectPermissionsTestCase):
    url = '/api/account/'
    patch_object_owners = patch(
        'users.models.CustomUser.objects',
        BaseHasObjectPermissionsTestCase.object_owners,
    )

    def setUp(self):
        self.permission = permissions.AuthenticatedAdminOrOwnerUser()
        self.object_owners.clear()
        self.request = MagicMock(user=MagicMock())
        self.view = MagicMock()

    def test_user_viewset_returns_200_for_object_owner_user(self):
        user_and_password = self.create_user(CustomUser.UserType.EMPLOYEE.name)
        url = self.url + str(user_and_password[0].pk) + '/'
        response = self.get_viewset_as(
            url,
            *user_and_password,
        )
        self.assertEqual(response.status_code, 200)

    def test_user_viewset_returns_403_for_not_object_owner_user(self):
        user_and_password = self.create_user(CustomUser.UserType.EMPLOYEE.name)
        url = self.url + str(user_and_password[0].pk) + '/'
        response = self.get_viewset_as(
            url,
            *self.create_user(CustomUser.UserType.EMPLOYEE.name),
        )
        self.assertEqual(response.status_code, 403)

    def test_user_viewset_returns_200_for_admin_type_user(self):
        user_and_password = self.create_user(CustomUser.UserType.EMPLOYEE.name)
        url = self.url + str(user_and_password[0].pk) + '/'
        response = self.get_viewset_as(
            url,
            *self.create_user(CustomUser.UserType.ADMIN.name),
        )
        self.assertEqual(response.status_code, 200)

    def test_user_viewset_returns_403_for_non_admin_type_user(self):
        user_and_password = self.create_user(CustomUser.UserType.EMPLOYEE.name)
        url = self.url + str(user_and_password[0].pk) + '/'
        response = self.get_viewset_as(
            url,
            *self.create_user(CustomUser.UserType.EMPLOYEE.name),
        )
        self.assertEqual(response.status_code, 403)
        response = self.get_viewset_as(
            url,
            *self.create_user(CustomUser.UserType.MANAGER.name),
        )
        self.assertEqual(response.status_code, 403)

    def test_permissions_Authenticated_Admin_Or_Owner_User_returns_false_for_non_admin_type_user(self):
        with self.patch_object_owners:
            obj = MagicMock()
            self.create_object_owner(CustomUser.UserType.EMPLOYEE.name)
        self.assertFalse(self.permission.has_object_permission(self.request, self.view, obj))
