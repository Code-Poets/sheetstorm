from django.core.exceptions import ValidationError
from django.test import TestCase
from parameterized import parameterized

import users.common.utils
import users.common.validators
from users.common.strings import ValidationErrorText


class TestCustomModelEmailValidationFunction(TestCase):
    @parameterized.expand(
        [
            ("testusercodepoets.it", ValidationErrorText.VALIDATION_ERROR_EMAIL_AT_SIGN_MESSAGE),
            ("@codepoets.it", ValidationErrorText.VALIDATION_ERROR_EMAIL_MALFORMED_FIRST_PART),
            ("testuser@invaliddomain.com", ValidationErrorText.VALIDATION_ERROR_EMAIL_MESSAGE_DOMAIN),
        ]
    )
    def test_user_could_not_be_created_with_wrong_data_in_email(self, email, message):
        with self.assertRaises(ValidationError) as exception:
            users.common.utils.custom_validate_email_function(email)
        self.assertEqual(message, exception.exception.message)
