import datetime
import mock

from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator
from django.test import TestCase

from users.common import constants
from users.common.exceptions import CustomValidationError
from users.common.strings import CustomUserModelText
from users.common.strings import CustomValidationErrorText
from users.common.utils import create_user_using_full_clean_and_save
from users.common.utils import generate_random_string_from_letters_and_digits
from users.models import CustomUser
from utils.base_tests import BaseModelTestCase


class TestCustomUserModel(TestCase):
    def test_that_create_user_method_should_raise_custom_validation_error_when_email_is_none(self):
        with self.assertRaises(CustomValidationError) as custom_exception:
            CustomUser.objects._create_user(
                None,
                "testuserpasswd",
                False,
                False,
                CustomUser.UserType.EMPLOYEE.name,
            )
        self.assertEqual(CustomValidationErrorText.VALIDATION_ERROR_EMAIL_MESSAGE, str(custom_exception.exception))

    def test_that_create_user_method_should_raise_custom_validation_error_when_password_is_none(self):
        with self.assertRaises(CustomValidationError) as custom_exception:
            CustomUser.objects._create_user(
                "testuser@codepoets.it",
                None,
                False,
                False,
                CustomUser.UserType.EMPLOYEE.name,
            )
        self.assertEqual(CustomValidationErrorText.VALIDATION_ERROR_PASSWORD_MESSAGE, str(custom_exception.exception))

    def test_user_create_superuser_method_should_create_user_with_admin_attributes(self):
        user = CustomUser.objects.create_superuser(
            "testadminuser@codepoets.it",
            'testadminuserpasswd',
        )
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertEqual(user.user_type, CustomUser.UserType.ADMIN.name)

    def test_user_with_existing_email_full_clean_should_raise_validation_error(self):
        create_user_using_full_clean_and_save(
            'testuser@codepoets.it',
            '',
            '',
            '',
            'newuserpasswd',
        )
        with self.assertRaises(ValidationError) as exception:
            create_user_using_full_clean_and_save(
                'testuser@codepoets.it',
                '',
                '',
                '',
                'newuserpasswd',
            )
        self.assertTrue(CustomValidationErrorText.VALIDATION_ERROR_EMAIL_EXISTING_MESSAGE in str(exception.exception))

    def test_user_with_email_without_at_least_one_at_sign_full_clean_should_raise_custom_validation_error(self):
        with self.assertRaises(CustomValidationError) as custom_exception:
            create_user_using_full_clean_and_save(
                'wrongtestusercodepoets.it',
                '',
                '',
                '',
                'newuserpasswd',
            )
        self.assertEqual(
            CustomValidationErrorText.VALIDATION_ERROR_EMAIL_AT_SIGN_MESSAGE,
            str(custom_exception.exception),
        )

    def test_user_with_first_name_longer_than_FIRST_NAME_MAX_LENGTH_full_clean_should_raise_validation_error(self):
        with self.assertRaises(ValidationError) as exception:
            create_user_using_full_clean_and_save(
                'testuser@codepoets.it',
                'a' * (constants.FIRST_NAME_MAX_LENGTH + 1),
                '',
                '',
                'newuserpasswd',
            )
        self.assertTrue(str(MaxLengthValidator.message) in str(exception.exception))

    def test_user_with_last_name_longer_than_LAST_NAME_MAX_LENGTH_full_clean_should_raise_validation_error(self):
        with self.assertRaises(ValidationError) as exception:
            create_user_using_full_clean_and_save(
                'testuser@codepoets.it',
                '',
                'a' * (constants.LAST_NAME_MAX_LENGTH + 1),
                '',
                'newuserpasswd',
            )
        self.assertTrue(str(MaxLengthValidator.message) in str(exception.exception))

    def test_user_with_phone_number_longer_than_PHONE_NUMBER_MAX_LENGTH_full_clean_should_raise_validation_error(self):
        with self.assertRaises(ValidationError) as exception:
            create_user_using_full_clean_and_save(
                'testuser@codepoets.it',
                '',
                '',
                '1' * (constants.PHONE_NUMBER_MAX_LENGTH + 1),
                'newuserpasswd',
            )
        self.assertTrue(str(CustomUserModelText.PHONE_REGEX_MESSAGE) in str(exception.exception))

    def test_user_with_phone_number_shorter_than_PHONE_NUMBER_MIN_LENGTH_full_clean_should_raise_validation_error(self):
        with self.assertRaises(ValidationError) as exception:
            create_user_using_full_clean_and_save(
                'testuser@codepoets.it',
                '',
                '',
                '1' * (constants.PHONE_NUMBER_MIN_LENGTH - 1),
                'newuserpasswd',
            )
        self.assertTrue(str(CustomUserModelText.PHONE_REGEX_MESSAGE) in str(exception.exception))

    def test_user_with_phone_number_with_non_digits_signs_should_raise_validation_error(self):
        with self.assertRaises(ValidationError) as exception:
            create_user_using_full_clean_and_save(
                'testuser@codepoets.it',
                '',
                '',
                generate_random_string_from_letters_and_digits(constants.PHONE_NUMBER_MIN_LENGTH),
                'newuserpasswd',
            )
        self.assertTrue(str(CustomUserModelText.PHONE_REGEX_MESSAGE) in str(exception.exception))


class TestCustomUserModelMethods(TestCase):
    def setUp(self):
        self.user = create_user_using_full_clean_and_save(
            "testuser@codepoets.it",
            "testusername",
            "testuserlastname",
            "",
            "testuserpasswd",
        )

    def test_that_get_absolute_url_method_should_return_absolute_url_with_users_email(self):
        stored_user = CustomUser.objects.get(email=self.user.email)
        self.assertEqual(stored_user.get_absolute_url(), f"/users/{self.user.email}/")

    def test_that_get_full_name_method_should_return_first_and_last_user_name_with_space_between(self):
        stored_user = CustomUser.objects.get(email=self.user.email)
        self.assertEqual(stored_user.get_full_name(), f"{stored_user.first_name} {stored_user.last_name}")

    def test_that_get_short_name_method_should_return_user_first_name(self):
        stored_user = CustomUser.objects.get(email=self.user.email)
        self.assertEqual(stored_user.get_short_name(), stored_user.first_name)

    def test_that_email_user_should_send_email_to_self_user(self):
        stored_user = CustomUser.objects.get(email=self.user.email)
        with mock.patch('users.models.CustomUser.email_user') as mocked_method:
            stored_user.email_user(
                'Subject of mail',
                'Some message to user: ' + stored_user.email,
                'from_email@codepoets.it',
            )
            stored_user.email_user.return_value = 'Email has been sent successfully'
        mocked_method.assert_called_once_with(
            'Subject of mail',
            'Some message to user: ' + stored_user.email,
            'from_email@codepoets.it',
        )
        self.assertTrue(mocked_method.called)
        self.assertEqual(mocked_method.call_count, 1)
        self.assertEqual(mocked_method(), 'Email has been sent successfully')


class TestCustomUserModelField(BaseModelTestCase):
    model_class = CustomUser
    required_input = {
        'email': 'example@codepoets.it',
        'first_name': 'Jan',
        'last_name': 'Kowalski',
        'date_of_birth': datetime.datetime.now().date(),
        'phone_number': '123456789',
        'country': 'PL',
        'user_type': 'EMPLOYEE',
        'password': 'passwduser',
    }

    def test_customuser_model_email_field_should_accept_correct_input(self):
        self.field_should_accept_input('email', 'user@codepoets.it')

    def test_customuser_model_email_field_should_not_accept_string_longer_than_set_limit(self):
        self.field_should_not_accept_input(
            'email',
            'a' * (constants.EMAIL_MAX_LENGTH - 12) + '@' + constants.VALID_EMAIL_DOMAIN_LIST[0]
        )

    def test_customuser_model_first_name_field_should_accept_correct_input(self):
        self.field_should_accept_input('first_name', 'Userfirstname')

    def test_customuser_model_first_name_field_may_be_empty(self):
        self.field_should_accept_null('first_name')

    def test_customuser_model_first_name_field_should_not_accept_string_longer_than_set_limit(self):
        self.field_should_not_accept_input('first_name', 'a' * (constants.FIRST_NAME_MAX_LENGTH + 1))

    def test_customuser_model_last_name_field_should_accept_correct_input(self):
        self.field_should_accept_input('last_name', 'Userlastname')

    def test_customuser_model_last_name_field_may_be_empty(self):
        self.field_should_accept_null('last_name')

    def test_customuser_model_last_name_field_should_not_accept_string_longer_than_set_limit(self):
        self.field_should_not_accept_input('last_name', 'a' * (constants.LAST_NAME_MAX_LENGTH + 1))

    def test_customuser_model_is_staff_field_should_have_default_value(self):
        self.field_should_have_non_null_default(field='is_staff', value=False)

    def test_customuser_model_is_active_field_should_have_default_value(self):
        self.field_should_have_non_null_default(field='is_active', value=True)

    def test_customuser_model_date_joined_field_should_be_filled_on_save(self):
        self.field_should_have_non_null_default('date_joined')

    def test_customuser_model_date_of_birth_field_should_accept_correct_input(self):
        self.field_should_accept_input('date_of_birth', datetime.datetime.now().date())

    def test_customuser_model_date_of_birth_field_may_be_empty(self):
        self.field_should_accept_null('date_of_birth')

    def test_customuser_model_updated_at_field_should_be_filled_on_save(self):
        self.field_should_have_non_null_default('updated_at')

    def test_customuser_model_phone_number_field_should_accept_correct_input(self):
        self.field_should_accept_input('phone_number', '123654789')

    def test_customuser_model_phone_number_field_may_be_empty(self):
        self.field_should_accept_null('phone_number')

    def test_customuser_model_phone_number_field_should_not_accept_decimal_longer_than_set_limit(self):
        self.field_should_not_accept_input('phone_number', '1' * (constants.PHONE_NUMBER_MAX_LENGTH + 1))

    def test_customuser_model_phone_number_field_should_not_accept_decimal_shorter_than_set_limit(self):
        self.field_should_not_accept_input('phone_number', '1' * (constants.PHONE_NUMBER_MIN_LENGTH - 1))

    def test_customuser_model_country_field_should_accept_correct_input(self):
        self.field_should_accept_input('country', 'GB')

    def test_customuser_model_country_field_may_be_empty(self):
        self.field_should_accept_null('country')

    def test_customuser_model_user_type_field_should_accept_correct_input(self):
        self.field_should_accept_input('user_type', 'EMPLOYEE')

    def test_customuser_model_password_field_should_accept_correct_input(self):
        self.field_should_accept_input('password', 'password')
