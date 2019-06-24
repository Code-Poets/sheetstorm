from django.shortcuts import reverse
from django.test import TestCase
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from freezegun import freeze_time

from users.common import constants
from users.common.strings import ValidationErrorText
from users.common.utils import generate_random_phone_number
from users.factories import AdminUserFactory
from users.factories import UserFactory
from users.models import CustomUser
from users.tokens import account_activation_token
from users.views import SignUp


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
        self.assertContains(response, self.user_admin.get_user_type_display())
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
        self.user = AdminUserFactory()
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


class UserUpdateTests(TestCase):
    def setUp(self):
        self.user = CustomUser(
            email="testuser@codepoets.it",
            password="newuserpasswd",
            first_name="John",
            last_name="Doe",
            country="PL",
            phone_number="123456789",
            is_active=True,
        )
        self.user.full_clean()
        self.user.save()
        self.client.force_login(self.user)

    def test_user_update_view_should_display_user_details_on_get(self):
        response = self.client.get(path=reverse("custom-user-update"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.last_name)

    def test_user_update_view_should_update_user_on_post(self):
        old_phone_number = self.user.phone_number
        new_phone_number = generate_random_phone_number(constants.PHONE_NUMBER_MIN_LENGTH)
        response = self.client.get(path=reverse("custom-user-update"))
        self.assertContains(response, old_phone_number)

        response = self.client.post(path=reverse("custom-user-update"), data={"phone_number": new_phone_number})
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(new_phone_number, self.user.phone_number)

    def test_user_update_view_should_not_update_user_on_post_if_form_is_invalid(self):
        phone_number_before_request = self.user.phone_number
        new_phone_number = generate_random_phone_number(constants.PHONE_NUMBER_MIN_LENGTH - 1)
        response = self.client.post(path=reverse("custom-user-update"), data={"phone_number": new_phone_number})
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(phone_number_before_request, self.user.phone_number)


class UserUpdateByAdminTests(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.user.full_clean()
        self.user.save()
        self.user_admin = AdminUserFactory()
        self.client.force_login(self.user_admin)
        self.correct_url = reverse("custom-user-update-by-admin", args=(self.user.pk,))

    def test_user_update_by_admin_view_should_display_user_details_on_get(self):
        response = self.client.get(path=reverse("custom-user-update-by-admin", args=(self.user.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.email)
        self.assertContains(response, self.user.first_name)
        self.assertContains(response, self.user.last_name)
        self.assertTemplateUsed("user_detail.html")

    def test_user_update_by_admin_view_should_not_render_non_existing_user(self):
        not_existing_pk = 1000
        response = self.client.get(path=reverse("custom-user-update-by-admin", args=(not_existing_pk,)))
        self.assertEqual(response.status_code, 404)

    def test_user_update_by_admin_view_should_update_user_on_post(self):
        new_phone_number = generate_random_phone_number(constants.PHONE_NUMBER_MIN_LENGTH)
        response = self.client.post(path=self.correct_url, data=self._get_user_data(new_phone_number))
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(new_phone_number, self.user.phone_number)

    def test_user_update_by_admin_view_should_not_update_user_on_post_if_form_is_invalid(self):
        phone_number_before_request = self.user.phone_number
        invalid_phone_number = generate_random_phone_number(constants.PHONE_NUMBER_MIN_LENGTH - 1)
        response = self.client.post(path=self.correct_url, data=self._get_user_data(invalid_phone_number))
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(phone_number_before_request, self.user.phone_number)

    def _get_user_data(self, new_phone_number):
        return {
            "email": self.user.email,
            "phone_number": new_phone_number,
            "user_type": CustomUser.UserType.EMPLOYEE.name,
        }


class SignUpTests(TestCase):
    def setUp(self):
        self.user = CustomUser(email="testuser@codepoets.it", first_name="John", last_name="Doe", password="passwduser")
        self.user.full_clean()
        self.non_existent_user_id = 999

    def _register_user_using_signup_view(self):
        return self.client.post(
            path=reverse("signup"),
            data={
                "email": self.user.email,
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "password1": self.user.password,
                "password2": self.user.password,
            },
        )

    def test_signup_view_should_display_signup_form_on_get(self):
        response = self.client.get(reverse("signup"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, SignUp.template_name)

    def test_signup_view_should_add_new_user_on_post(self):
        self.assertEqual(CustomUser.objects.all().count(), 0)
        response = self._register_user_using_signup_view()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("success-signup"))
        self.assertEqual(CustomUser.objects.all().count(), 1)
        self.assertEqual(CustomUser.objects.get(email=self.user.email).is_active, False)

    def test_that_registered_user_must_activate_account_by_activation_link(self):
        with freeze_time("2019-06-07 07:07:07"):
            self.assertEqual(CustomUser.objects.all().count(), 0)
            response = self._register_user_using_signup_view()
            self.assertEqual(response.status_code, 302)
            self.assertEqual(CustomUser.objects.get(email=self.user.email).is_active, False)
            user = CustomUser.objects.get(email=self.user.email)
            url = reverse(
                "activate",
                args=(urlsafe_base64_encode(force_bytes(user.pk)), account_activation_token.make_token(user)),
            )
            response = self.client.get(path=url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(CustomUser.objects.get(email=self.user.email).is_active, True)

    def test_that_registered_user_with_wrong_activation_link_will_not_activate_account(self):
        with freeze_time("2019-06-07 07:07:07"):
            self.assertEqual(CustomUser.objects.all().count(), 0)
            response = self._register_user_using_signup_view()
            self.assertEqual(response.status_code, 302)
            self.assertEqual(CustomUser.objects.get(email=self.user.email).is_active, False)
            user = CustomUser.objects.get(email=self.user.email)
            url = reverse(
                "activate",
                args=(
                    urlsafe_base64_encode(force_bytes(self.non_existent_user_id)),
                    account_activation_token.make_token(user),
                ),
            )
            response = self.client.get(path=url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(CustomUser.objects.get(email=self.user.email).is_active, False)
