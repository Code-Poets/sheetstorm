from users.common import constants
from users.common.utils import create_user_using_full_clean_and_save
from users.serializers import UserSerializer
from users.serializers import CustomRegisterSerializer
from utils.base_tests import BaseSerializerTestCase

import datetime


class TestUserSerializerField(BaseSerializerTestCase):
    serializer_class = UserSerializer
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

    def test_user_serializer_email_field_should_accept_correct_input(self):
        self.field_should_accept_input('email', 'testuser@codepoets.it')

    def test_user_serializer_email_field_should_not_accept_string_longer_than_set_limit(self):
        self.field_should_not_accept_input(
            'email',
            'a' * (constants.EMAIL_MAX_LENGTH - 12) + '@' + constants.VALID_EMAIL_DOMAIN_LIST[0]
        )

    def test_user_serializer_first_name_field_should_accept_correct_input(self):
        self.field_should_accept_input('first_name', 'Userfirstname')

    def test_user_serializer_first_name_field_should_not_accept_string_longer_than_set_limit(self):
        self.field_should_not_accept_input('first_name', 'a' * (constants.FIRST_NAME_MAX_LENGTH + 1))

    def test_user_serializer_last_name_field_should_accept_correct_input(self):
        self.field_should_accept_input('last_name', 'Userlastname')

    def test_user_serializer_last_name_field_should_not_accept_string_longer_than_set_limit(self):
        self.field_should_not_accept_input('last_name', 'a' * (constants.LAST_NAME_MAX_LENGTH + 1))

    def test_user_serializer_date_of_birth_field_should_accept_correct_input(self):
        self.field_should_accept_input('date_of_birth', datetime.datetime.now().date())

    def test_user_serializer_date_of_birth_field_may_be_empty(self):
        self.field_should_accept_null('date_of_birth')

    def test_user_serializer_phone_number_field_should_accept_correct_input(self):
        self.field_should_accept_input('phone_number', '123654789')

    def test_user_serializer_phone_number_field_may_be_empty(self):
        self.field_should_accept_null('phone_number')

    def test_user_serializer_phone_number_field_should_not_accept_decimal_longer_than_set_limit(self):
        self.field_should_not_accept_input('phone_number', '1' * (constants.PHONE_NUMBER_MAX_LENGTH + 1))

    def test_user_serializer_phone_number_field_should_not_accept_decimal_shorter_than_set_limit(self):
        self.field_should_not_accept_input('phone_number', '1' * (constants.PHONE_NUMBER_MIN_LENGTH - 1))

    def test_user_serializer_country_field_should_accept_correct_input(self):
        self.field_should_accept_input('country', 'GB')

    def test_user_serializer_user_type_field_should_accept_correct_input(self):
        self.field_should_accept_input('user_type', 'EMPLOYEE')

    def test_user_serializer_password_field_should_accept_correct_input(self):
        self.field_should_accept_input('password', 'password')


class TestCustomRegisterSerializerField(BaseSerializerTestCase):
    serializer_class = CustomRegisterSerializer
    required_input = {
        'email': 'example@codepoets.it',
        'first_name': 'Jan',
        'last_name': 'Kowalski',
        'password': 'passwduser',
        'password_confirmation': 'passwduser',
    }

    def test_register_serializer_email_field_should_accept_correct_input(self):
        self.field_should_accept_input('email', 'testuser@codepoets.it')

    def test_register_serializer_email_field_should_be_unique(self):
        create_user_using_full_clean_and_save('testuser@codepoets.it', '', '', '', 'newuserpasswd')
        self.field_should_not_accept_input('email', 'testuser@codepoets.it')

    def test_register_serializer_password_should_equal_password_confirmation(self):
        self.field_should_not_accept_input('password_confirmation', 'anotherpasswduser')
