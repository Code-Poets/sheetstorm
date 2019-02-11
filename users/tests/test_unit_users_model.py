from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator
from django.test import TestCase

from users.common.exceptions import CustomValidationError
from users.common.strings import CustomUserModelText
from users.common.strings import CustomValidationErrorText
from users.common import constants
from users.models import CustomUser


class TestCustomUserModel(TestCase):
    def test_user_should_hold_email_address(self):
        with self.assertRaisesRegex(
            CustomValidationError,
            CustomValidationErrorText.VALIDATION_ERROR_EMAIL_MESSAGE,
        ):
            CustomUser.objects._create_user(
                None,
                "testuserpasswd",
                False,
                False,
                CustomUser.UserType.EMPLOYEE.name,
            )

    def test_user_should_hold_password(self):
        with self.assertRaisesRegex(
            CustomValidationError,
            CustomValidationErrorText.VALIDATION_ERROR_PASSWORD_MESSAGE,
        ):
            CustomUser.objects._create_user(
                "testuser@codepoets.it",
                None,
                False,
                False,
                CustomUser.UserType.EMPLOYEE.name,
            )

    def test_user_should_not_hold_same_email_as_another_user(self):
        CustomUser.objects.create(
            email="testuser@codepoets.it",
            password='newuserpasswd',
        )
        new_user = CustomUser(
            email="testuser@codepoets.it",
            password='newuserpasswd',
        )
        with self.assertRaisesRegex(
            ValidationError,
            CustomValidationErrorText.VALIDATION_ERROR_EMAIL_EXISTING_MESSAGE,
        ):
            new_user.full_clean()

    def test_user_should_not_hold_email_without_at_sign(self):
        new_user = CustomUser(
            email="wrongtestusercodepoets.it",
            password='newuserpasswd',
        )
        with self.assertRaisesRegex(
            CustomValidationError,
            CustomValidationErrorText.VALIDATION_ERROR_EMAIL_AT_SIGN_MESSAGE,
        ):
            new_user.full_clean()

    def test_user_should_not_hold_first_name_longer_than_FIRST_NAME_MAX_LENGTH(self):
        new_user = CustomUser(
            email="testuser@codepoets.it",
            password='newuserpasswd',
            first_name='a' * (constants.FIRST_NAME_MAX_LENGTH + 1),
        )
        with self.assertRaisesRegex(
            ValidationError,
            str(MaxLengthValidator.message),
        ):
            new_user.full_clean()

    def test_user_should_not_hold_last_name_longer_than_LAST_NAME_MAX_LENGTH(self):
        new_user = CustomUser(
            email="testuser@codepoets.it",
            password='newuserpasswd',
            last_name='a' * (constants.LAST_NAME_MAX_LENGTH + 1),
        )
        with self.assertRaisesRegex(
            ValidationError,
            str(MaxLengthValidator.message),
        ):
            new_user.full_clean()

    def test_user_should_hold_phone_number_shorter_or_equal_to_PHONE_NUMBER_MAX_LENGTH(self):
        new_user = CustomUser(
            email="testuser@codepoets.it",
            password='newuserpasswd',
            phone_number="1" * (constants.PHONE_NUMBER_MAX_LENGTH + 1),
        )
        with self.assertRaisesRegex(
            ValidationError,
            str(CustomUserModelText.PHONE_REGEX_MESSAGE),
        ):
            new_user.full_clean()

    def test_user_should_hold_phone_number_longer_or_equal_to_PHONE_NUMBER_MIN_LENGTH(self):
        new_user = CustomUser(
            email="testuser@codepoets.it",
            password='newuserpasswd',
            phone_number="1" * (constants.PHONE_NUMBER_MIN_LENGTH - 1),
        )
        with self.assertRaisesRegex(
            ValidationError,
            str(CustomUserModelText.PHONE_REGEX_MESSAGE),
        ):
            new_user.full_clean()

    def test_user_should_hold_phone_number_with_all_digits(self):
        new_user = CustomUser(
            email="testuser@codepoets.it",
            password='newuserpasswd',
            phone_number="X" * constants.PHONE_NUMBER_MIN_LENGTH,
        )
        with self.assertRaisesRegex(
            ValidationError,
            str(CustomUserModelText.PHONE_REGEX_MESSAGE),
        ):
            new_user.full_clean()


class TestCustomUserModelMethods(TestCase):
    def setUp(self):
        CustomUser.objects.create(
            email="testuser@codepoets.it",
            first_name="testusername",
            last_name="testuserlastname",
        )

    def test_get_absolute_url_method_should_return_absolute_url_with_users_email(self):
        email = "testuser@codepoets.it"
        search_user = CustomUser.objects.get(email=email)
        self.assertEqual(
            search_user.get_absolute_url(),
            f"/users/{email}/",
        )

    def test_get_full_name_method_should_return_first_and_last_user_name_with_space_between(self):
        email = "testuser@codepoets.it"
        search_user = CustomUser.objects.get(email=email)
        self.assertEqual(
            search_user.get_full_name(),
            f"{search_user.first_name} {search_user.last_name}",
        )

    def test_get_short_name_method_should_return_user_first_name(self):
        email = "testuser@codepoets.it"
        search_user = CustomUser.objects.get(email=email)
        self.assertEqual(
            search_user.get_short_name(),
            search_user.first_name,
        )
