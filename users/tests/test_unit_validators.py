import datetime

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.test import override_settings
from freezegun import freeze_time
from parameterized import parameterized

from users.common.strings import ValidationErrorText
from users.validators import UserAgeValidator
from users.validators import UserEmailValidation


@freeze_time("2019-05-27")
class TestUserAgeValidator(TestCase):
    def setUp(self):
        self.user_age_validator = UserAgeValidator(
            UserAgeValidator.MINIMAL_ACCETABLE_AGLE, UserAgeValidator.MAXIMAL_ACCEPTABLE_AGE
        )

    def test_users_age_can_be_none(self):
        self._assert_date_of_birth_is_valid(None)

    def test_users_age_can_be_equal_to_lower_limit(self):
        # user is exactly 18 years old
        date_of_birth = datetime.datetime.strptime("2001-05-27", "%Y-%m-%d").date()
        self._assert_date_of_birth_is_valid(date_of_birth)

    def test_users_age_can_be_equal_to_upper_limit(self):
        # user is exactly 100 years old - 1 day (still 99)
        date_of_birth = datetime.datetime.strptime("1919-05-28", "%Y-%m-%d").date()
        self._assert_date_of_birth_is_valid(date_of_birth)

    def test_when_users_age_is_below_lower_limit_validation_error_is_raised(self):
        # user is exactly 18 years old - 1 day (still 17)
        date_of_birth = datetime.datetime.strptime("2001-05-28", "%Y-%m-%d").date()
        with self.assertRaises(ValidationError):
            self.user_age_validator(date_of_birth)

    def test_when_users_age_is_above_upper_limit_validation_error_is_raised(self):
        # user is exactly 100 years old
        date_of_birth = datetime.datetime.strptime("1919-05-27", "%Y-%m-%d").date()
        with self.assertRaises(ValidationError):
            self.user_age_validator(date_of_birth)

    def _assert_date_of_birth_is_valid(self, date_of_birth):
        try:
            self.user_age_validator(date_of_birth)
        except Exception as e:  # pylint:disable=broad-except
            self.fail(f"Unexpected exception {str(e)} has occurred!")


class TestUserEmailValidation(TestCase):
    def setUp(self) -> None:
        self.user_email_validation = UserEmailValidation()

    @parameterized.expand(
        [
            ("testusercodepoets.it", ValidationErrorText.VALIDATION_ERROR_EMAIL_AT_SIGN_MESSAGE),
            ("@codepoets.it", ValidationErrorText.VALIDATION_ERROR_EMAIL_MALFORMED_FIRST_PART),
            ("testuser@invaliddomain.com", ValidationErrorText.VALIDATION_ERROR_EMAIL_MESSAGE_DOMAIN),
        ]
    )
    def test_validator_should_throw_exception_with_invalid_email(self, email, exception_message):
        with self.assertRaises(ValidationError) as exception:
            self.user_email_validation(email)
        self.assertEqual(exception_message, exception.exception.message)

    @parameterized.expand(
        [("valid@codepoets.it", ["codepoets.it"]), ("valid@fewdomains.it", ["test.pl", "fewdomains.it"])]
    )
    def test_validator_should_allow_all_email_domains_with_empty_valid_domain_list(self, email, valid_email_domains):
        with override_settings(VALID_EMAIL_DOMAIN_LIST=valid_email_domains):
            valid_email = self.user_email_validation(email)
        self.assertEqual(valid_email, email)

    @parameterized.expand(["valid@codepoets.it", "valid@otherdomain.it"])
    def test_validator_all_domain_are_not_allowed_if_valid_email_domain_list_is_empty(self, email):
        with override_settings(VALID_EMAIL_DOMAIN_LIST=[]):
            with self.assertRaises(ValidationError):
                self.user_email_validation(email)
