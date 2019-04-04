from django.test import TestCase

from users.models import CustomUser


class TestCustomUserLogin(TestCase):
    def setUp(self):
        self.user_type = CustomUser.UserType.EMPLOYEE.name
        CustomUser.objects._create_user("testuser@codepoets.it", "testuserpasswd", False, False, self.user_type)

    def test_user_client_should_log_in_with_correct_email_and_password(self):
        self.assertTrue(self.client.login(email="testuser@codepoets.it", password="testuserpasswd"))

    def test_user_client_should_not_log_in_with_wrong_email(self):
        self.assertFalse(self.client.login(email="wrongtestuser@codepoets.it", password="testuserpasswd"))

    def test_user_client_should_not_log_in_with_wrong_password(self):
        self.assertFalse(self.client.login(email="testuser@codepoets.it", password="wrongtestuserpasswd"))

    def test_user_client_should_not_log_in_when_email_is_none(self):
        self.assertFalse(self.client.login(email=None, password="wrongtestuserpasswd"))

    def test_user_client_should_not_log_in_when_password_is_none(self):
        self.assertFalse(self.client.login(email="testuser@codepoets.it", password=None))
