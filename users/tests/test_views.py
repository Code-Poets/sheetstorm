from django.test import TestCase
from rest_framework.reverse import reverse

from users.common.strings import ValidationErrorText
from users.factories import UserFactory
from users.models import CustomUser


class ChangePasswordTests(TestCase):
    def setUp(self):
        self.user_password = "userpasswd"
        self.user = UserFactory()

    def test_change_user_password_view_should_change_user_password_on_post(self):
        data = {"old_password": self.user_password, "new_password1": "newuserpasswd", "new_password2": "newuserpasswd"}
        self.client.login(email=self.user.email, password=self.user_password)
        response = self.client.post(reverse("password_change"), data)
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.user.check_password(data["new_password1"]))

    def test_change_user_password_view_should_not_change_user_password_when_old_password_is_incorrect(self):
        data = {"old_password": "wronguserpasswd", "new_password1": "newuserpasswd", "new_password2": "newuserpasswd"}
        self.client.login(email=self.user.email, password=self.user_password)
        response = self.client.post(reverse("password_change"), data)
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.user.check_password(data["new_password1"]))
        self.assertFalse(self.user.check_password(data["old_password"]))
        self.assertTrue(self.user.check_password(self.user_password))

    def test_change_user_password_view_should_not_change_user_password_when_new_passwords_does_not_match(self):
        data = {
            "old_password": self.user_password,
            "new_password1": "newuserpasswd",
            "new_password2": "notthesamenewuserpasswd",
        }
        self.client.login(email=self.user.email, password=self.user_password)
        response = self.client.post(reverse("password_change"), data)
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            ValidationErrorText.VALIDATION_ERROR_SIGNUP_PASSWORD_MESSAGE
            in response.context["form"].errors.get("new_password2")
        )
        self.assertFalse(self.user.check_password(data["new_password1"]))
        self.assertTrue(self.user.check_password(data["old_password"]))


class UserListTests(TestCase):
    def setUp(self):
        self.user_admin = UserFactory(user_type=CustomUser.UserType.ADMIN.name)
        self.user_admin.full_clean()
        self.user_admin.save()
        self.user_manager = UserFactory(user_type=CustomUser.UserType.MANAGER.name)
        self.user_manager.full_clean()
        self.user_manager.save()
        self.user_employee = UserFactory(user_type=CustomUser.UserType.EMPLOYEE.name)
        self.user_employee.full_clean()
        self.user_employee.save()
        self.url = reverse("custom-users-list")

    def test_user_list_view_should_display_users_list_on_get(self):
        self.client.force_login(self.user_admin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user_admin.user_type)
        self.assertContains(response, self.user_admin.email)
        self.assertContains(response, self.user_admin.first_name)
        self.assertContains(response, self.user_admin.last_name)

    def test_user_list_view_should_not_be_accessible_for_unauthenticated_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_user_employee_should_not_get_list_of_all_employees(self):
        self.client.force_login(self.user_employee)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_user_manager_should_not_get_list_of_all_employees(self):
        self.client.force_login(self.user_manager)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)


class UserCreateTests(TestCase):
    def setUp(self):
        self.user = CustomUser(
            email="testuser@codepoets.it", password="newuserpasswd", first_name="John", last_name="Doe", country="PL"
        )
        self.user.full_clean()
        self.user.save()
        self.url = reverse("custom-user-create")
        self.client.force_login(self.user)

    def test_user_create_view_should_display_create_user_form_on_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create new employee")

    def test_user_create_view_should_add_new_user_on_post(self):
        response = self.client.post(
            path=reverse("custom-user-create"),
            data={
                "email": "anothertestuser@codepoets.it",
                "password1": "this_is_a_pass",
                "password2": "this_is_a_pass",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/users/")
        self.assertEqual(CustomUser.objects.all().count(), 2)

    def test_user_create_view_should_not_add_new_user_on_post_if_form_is_invalid(self):
        response = self.client.post(path=reverse("custom-user-create"), data={"email": "testuser@codepoets.it"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(CustomUser.objects.all().count(), 1)
