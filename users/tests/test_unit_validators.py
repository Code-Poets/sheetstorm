import datetime

from django.core.exceptions import ValidationError
from django.test import TestCase
from freezegun import freeze_time

from users.validators import UserAgeValidator


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
