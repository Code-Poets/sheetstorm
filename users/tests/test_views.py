from django.test import TestCase
from rest_framework.reverse import reverse

from users.common.strings import CustomValidationErrorText
from users.factories import UserFactory


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
            CustomValidationErrorText.VALIDATION_ERROR_SIGNUP_PASSWORD_MESSAGE
            in response.context["form"].errors.get("new_password2")
        )
        self.assertFalse(self.user.check_password(data["new_password1"]))
        self.assertTrue(self.user.check_password(data["old_password"]))
