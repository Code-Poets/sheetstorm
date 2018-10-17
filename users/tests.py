from django.test import TestCase
from users.models import CustomUser
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.core.validators import MaxLengthValidator
from users.common.exceptions import CustomValidationError
from users.common.strings import CustomValidationErrorText
from users.common.strings import CustomUserModelText
from users.common import constants


class TestCustomUserLogin(TestCase):
    def setUp(self):
        CustomUser.objects._create_user(
            "testuser@example.com",
            "testuserpasswd",
            False,
            False,
        )

    def test_user_should_login_correctly(self):
        self.assertTrue(self.client.login(
            email="testuser@example.com",
            password="testuserpasswd",
            )
        )

    def test_user_should_not_login_correctly_with_wrong_email(self):
        self.assertFalse(self.client.login(
            email="wrongtestuser@example.com",
            password="testuserpasswd",
            )
        )

    def test_user_should_not_login_correctly_with_wrong_password(self):
        self.assertFalse(self.client.login(
            email="testuser@example.com",
            password="wrongtestuserpasswd",
            )
        )

    def test_user_should_not_login_correctly_with_no_email(self):
        self.assertFalse(self.client.login(
            email=None,
            password="wrongtestuserpasswd",
            )
        )

    def test_user_should_not_login_correctly_with_no_password(self):
        self.assertFalse(self.client.login(
            email="testuser@example.com",
            password=None,
            )
        )


class TestCustomUserModel(TestCase):
    def test_user_should_hold_email_address(self):
        with self.assertRaisesRegexp(
            CustomValidationError,
            CustomValidationErrorText.VALIDATION_ERROR_EMAIL_MESSAGE,
        ):
            CustomUser.objects._create_user(None,"testuserpasswd",False,False)

    def test_user_should_hold_password(self):
        with self.assertRaisesRegexp(
            CustomValidationError,
            CustomValidationErrorText.VALIDATION_ERROR_PASSWORD_MESSAGE,
        ):
            CustomUser.objects._create_user("testuser@example.com",None,False,False)

    def test_user_should_not_hold_same_email_as_another_user(self):
        old_user = CustomUser.objects.create(
            email = "testuser@example.com",
            password = 'newuserpasswd',
        )
        new_user = CustomUser(
            email = "testuser@example.com",
            password = 'newuserpasswd',
        )
        with self.assertRaisesRegexp(
            ValidationError,
            "User with this Email address already exists.",
        ):
            new_user.full_clean()

    def test_user_should_not_hold_email_without_at_sign(self):
        new_user = CustomUser(
            email = "wrongtestuserexample.com",
            password = 'newuserpasswd',
        )
        with self.assertRaisesRegexp(
            ValidationError,
            str(EmailValidator.message),
        ):
            new_user.full_clean()

    def test_user_should_not_hold_first_name_longer_than_FIRST_NAME_MAX_LENGTH(self):
        new_user = CustomUser(
            email = "testuser@example.com",
            password = 'newuserpasswd',
            first_name = 'a'*(constants.FIRST_NAME_MAX_LENGTH+1),
        )
        with self.assertRaisesRegexp(
            ValidationError,
            str(MaxLengthValidator.message),
        ):
            new_user.full_clean()

    def test_user_should_not_hold_last_name_longer_than_LAST_NAME_MAX_LENGTH(self):
        new_user = CustomUser(
            email = "testuser@example.com",
            password = 'newuserpasswd',
            last_name = 'a'*(constants.LAST_NAME_MAX_LENGTH+1),
        )
        with self.assertRaisesRegexp(
            ValidationError,
            str(MaxLengthValidator.message),
        ):
            new_user.full_clean()

    def test_user_should_hold_phone_number_shorter_or_equal_to_PHONE_NUMBER_MAX_LENGTH(self):
        new_user = CustomUser (
            email = "testuser@example.com",
            password = 'newuserpasswd',
            phone_number = "1"*(constants.PHONE_NUMBER_MAX_LENGTH+1),
        )
        with self.assertRaisesRegexp(
            ValidationError,
            str(CustomUserModelText.PHONE_REGEX_MESSAGE),
        ):
            new_user.full_clean()

    def test_user_should_hold_phone_number_longer_or_equal_to_PHONE_NUMBER_MIN_LENGTH(self):
        new_user = CustomUser (
            email = "testuser@example.com",
            password = 'newuserpasswd',
            phone_number = "1"*(constants.PHONE_NUMBER_MIN_LENGTH-1),
        )
        with self.assertRaisesRegexp(
            ValidationError,
            str(CustomUserModelText.PHONE_REGEX_MESSAGE),
        ):
            new_user.full_clean()

    def test_user_should_hold_phone_number_with_all_digits(self):
        new_user = CustomUser (
            email = "testuser@example.com",
            password = 'newuserpasswd',
            phone_number = "X"*constants.PHONE_NUMBER_MIN_LENGTH,
        )
        with self.assertRaisesRegexp(
            ValidationError,
            str(CustomUserModelText.PHONE_REGEX_MESSAGE),
        ):
            new_user.full_clean()

class TestCustomUserModelMethods(TestCase):
    def setUp(self):
        new_user = CustomUser.objects.create(
            email="testuser@example.com",
            first_name="testusername",
            last_name="testuserlastname",
        )

    def test_get_absolute_url_method_should_return_absolute_url_with_users_email(self):
        email = "testuser@example.com"
        search_user = CustomUser.objects.get(email=email)
        self.assertEqual(
            search_user.get_absolute_url(),
            f"/users/{email}/",
        )

    def test_get_full_name_method_should_return_first_and_last_user_name_with_space_between(self):
        email = "testuser@example.com"
        search_user = CustomUser.objects.get(email=email)
        self.assertEqual(
            search_user.get_full_name(),
            f"{search_user.first_name} {search_user.last_name}",
        )

    def test_get_short_name_method_should_return_user_first_name(self):
        email = "testuser@example.com"
        search_user = CustomUser.objects.get(email=email)
        self.assertEqual(
            search_user.get_short_name(),
            search_user.first_name,
        )
