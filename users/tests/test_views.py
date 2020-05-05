from django.shortcuts import reverse
from django.test import TestCase
from django.test import override_settings
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from freezegun import freeze_time
from parameterized import parameterized

from employees.factories import ReportFactory
from managers.factories import ProjectFactory
from users.common.strings import UserNotificationsText
from users.common.strings import ValidationErrorText
from users.factories import AdminUserFactory
from users.factories import ManagerUserFactory
from users.factories import UserFactory
from users.models import CustomUser
from users.tokens import account_activation_token
from users.views import NotificationUserListView
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
        # Replacement between "’" and "'" it is caused because in response
        # we got "’" but from strings hardcoded in `strings.py` we got "'"
        self.assertEqual(
            response.context["form"].errors.get("new_password2")[0].replace("’", "'"),
            ValidationErrorText.VALIDATION_ERROR_SIGNUP_PASSWORD_MESSAGE,
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

    def test_inactive_user_should_not_be_lister(self):
        inactive_user = UserFactory(is_active=False)
        self.client.force_login(self.user_admin)
        response = self.client.get(self.url)
        self.assertNotContains(response, inactive_user.email)


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
        self.assertEqual(response.url, reverse("custom-users-list"))
        self.assertEqual(CustomUser.objects.all().count(), 2)

    def test_user_create_view_should_not_add_new_user_on_post_if_form_is_invalid(self):
        response = self.client.post(path=reverse("custom-user-create"), data={"email": "testuser@codepoets.it"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(CustomUser.objects.all().count(), 1)


class UserUpdateTests(TestCase):
    def setUp(self):
        self.user = CustomUser(
            email="testuser@codepoets.it", password="newuserpasswd", first_name="John", last_name="Doe", is_active=True
        )
        self.user.full_clean()
        self.user.save()
        self.client.force_login(self.user)

    def test_user_update_view_should_display_user_details_on_get(self):
        response = self.client.get(path=reverse("custom-user-update"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.last_name)

    def test_user_update_view_should_update_user_on_post(self):
        old_last_name = self.user.last_name
        new_last_name = "New Last Name"
        response = self.client.get(path=reverse("custom-user-update"))
        self.assertContains(response, old_last_name)

        response = self.client.post(path=reverse("custom-user-update"), data={"last_name": new_last_name})
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(new_last_name, self.user.last_name)

    def test_user_update_view_should_not_update_user_on_post_if_form_is_invalid(self):
        last_name_before_request = self.user.last_name
        invalid_last_name = "Last%$&Name"
        response = self.client.post(path=reverse("custom-user-update"), data={"last_name": invalid_last_name})
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(last_name_before_request, self.user.last_name)


class UserUpdateByAdminTests(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.user.full_clean()
        self.user.save()
        self.user_admin = AdminUserFactory()
        self.client.force_login(self.user_admin)
        self.data = {
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "email": self.user.email,
            "user_type": self.user.user_type,
        }
        self.correct_url = reverse("custom-user-update-by-admin", kwargs={"pk": self.user.pk})

    def test_user_update_by_admin_view_should_display_user_details_on_get(self):
        response = self.client.get(path=reverse("custom-user-update-by-admin", kwargs={"pk": self.user.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.email)
        self.assertContains(response, self.user.first_name)
        self.assertContains(response, self.user.last_name)
        self.assertTemplateUsed("user_detail.html")

    def test_user_update_by_admin_view_should_not_render_non_existing_user(self):
        response = self.client.get(path=reverse("custom-user-update-by-admin", kwargs={"pk": 1000}))
        self.assertEqual(response.status_code, 404)

    def test_user_update_by_admin_view_should_update_user_on_post(self):
        self.data["last_name"] = "NewLastName"
        response = self.client.post(self.correct_url, self.data)
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.data["last_name"], self.user.last_name)

    def test_user_update_by_admin_view_should_not_update_user_on_post_if_form_is_invalid(self):
        self.data["email"] = "admin@invalid.it"
        response = self.client.post(self.correct_url, self.data)
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 200)


@override_settings(EMAIL_SIGNUP_VERIFICATION=True)
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
                "captcha_0": "PASSED",
                "captcha_1": "PASSED",
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

    def test_registered_user_must_activate_account_by_activation_link(self):
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

    def test_registered_user_with_wrong_activation_link_will_not_activate_account(self):
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


class NotificationsTests(TestCase):
    def setUp(self):
        self.admin = AdminUserFactory()
        self.employee = UserFactory()
        self.manager = ManagerUserFactory()
        self.project = ProjectFactory()
        self.project.managers.add(self.admin)
        self.project.managers.add(self.manager)
        self.project.members.add(self.employee)
        self.url = reverse("custom-users-notifications")

    def _check_response(self, response, status_code, contains):
        self.assertTemplateUsed(response, NotificationUserListView.template_name)
        self.assertEqual(response.status_code, status_code)
        for element in contains:
            self.assertContains(response, element)

    @parameterized.expand(["2019-07-06", "2019-07-07", "2019-07-08"])
    def test_manager_should_not_get_any_notification_about_missing_reports(self, test_date):
        with freeze_time("2019-07-05"):
            ReportFactory(author=self.employee, project=self.project, date="2019-07-05")

        self.client.force_login(self.manager)
        with freeze_time(test_date):
            response = self.client.get(self.url)
        self._check_response(response, 200, [UserNotificationsText.NO_MORE_NOTIFICATIONS.value])

    @parameterized.expand([("2019-07-10", "<td>1</td>"), ("2019-07-11", "<td>2</td>"), ("2019-07-15", "<td>4</td>")])
    def test_manager_should_get_notification_about_missing_reports(self, test_date, missing_reports):
        with freeze_time("2019-07-08"):
            ReportFactory(author=self.employee, project=self.project, date="2019-07-08")

        self.client.force_login(self.manager)
        with freeze_time(test_date):
            response = self.client.get(self.url)
        self._check_response(response, 200, [self.employee.email, missing_reports])

    def test_manager_should_only_get_notifications_about_employees_from_his_projects(self):
        with freeze_time("2019-07-08"):
            ReportFactory(date="2019-07-08")

        self.client.force_login(self.manager)
        with freeze_time("2019-07-15"):
            response = self.client.get(self.url)
        self._check_response(response, 200, [UserNotificationsText.NO_MORE_NOTIFICATIONS.value])

    def test_manager_should_not_get_any_notifications_if_they_are_disabled_for_project(self):
        self.project.is_notification_enabled = False
        self.project.save()

        with freeze_time("2019-07-08"):
            ReportFactory(author=self.employee, project=self.project, date="2019-07-08")

        self.client.force_login(self.manager)
        with freeze_time("2019-07-15"):
            response = self.client.get(self.url)
        self._check_response(response, 200, [UserNotificationsText.NO_MORE_NOTIFICATIONS.value])

    def test_manager_should_not_get_get_notifications_about_inactive_employees(self):
        inactive_user = UserFactory(is_active=False)
        with freeze_time("2019-07-08"):
            ReportFactory(author=inactive_user, project=self.project, date="2019-07-08")

        self.client.force_login(self.manager)
        with freeze_time("2019-07-15"):
            response = self.client.get(self.url)
        self._check_response(response, 200, [UserNotificationsText.NO_MORE_NOTIFICATIONS.value])
