from django.test import TestCase
from rest_framework import serializers

from users.common import utils
from users.common.exceptions import CustomValidationError
from users.common.strings import CustomValidationErrorText
from users.serializers import CustomRegisterSerializer


class TestCustomModelEmailValidationFunction(TestCase):
    def test_user_email_should_hold_at_least_one_at_sign(self):
        email = "testusercodepoets.it"
        with self.assertRaises(CustomValidationError) as custom_exception:
            utils.custom_validate_email_function(self, email)
        self.assertEqual(
            CustomValidationErrorText.VALIDATION_ERROR_EMAIL_AT_SIGN_MESSAGE, str(custom_exception.exception)
        )

    def test_user_email_should_not_hold_malformed_first_part(self):
        email = "@codepoets.it"
        with self.assertRaises(CustomValidationError) as custom_exception:
            utils.custom_validate_email_function(self, email)
        self.assertEqual(
            CustomValidationErrorText.VALIDATION_ERROR_EMAIL_MALFORMED_FIRST_PART, str(custom_exception.exception)
        )

    def test_user_should_hold_email_with_valid_domain(self):
        email = "testuser@invaliddomain.com"
        with self.assertRaises(CustomValidationError) as custom_exception:
            utils.custom_validate_email_function(self, email)
        self.assertEqual(
            CustomValidationErrorText.VALIDATION_ERROR_EMAIL_MESSAGE_DOMAIN, str(custom_exception.exception)
        )


class TestCustomSerializerEmailValidationFunction(TestCase):
    def test_user_email_should_hold_at_least_one_at_sign(self):
        email = "testusercodepoets.it"
        with self.assertRaises(serializers.ValidationError) as serializer_exception:
            utils.custom_validate_email_function(CustomRegisterSerializer(), email)
        self.assertTrue(
            CustomValidationErrorText.VALIDATION_ERROR_EMAIL_AT_SIGN_MESSAGE in str(serializer_exception.exception)
        )

    def test_user_email_should_not_hold_malformed_first_part(self):
        email = "@codepoets.it"
        with self.assertRaises(serializers.ValidationError) as serializer_exception:
            utils.custom_validate_email_function(CustomRegisterSerializer(), email)
        self.assertTrue(
            CustomValidationErrorText.VALIDATION_ERROR_EMAIL_MALFORMED_FIRST_PART in str(serializer_exception.exception)
        )

    def test_user_should_hold_email_with_valid_domain(self):
        email = "testuser@invaliddomain.com"
        with self.assertRaises(serializers.ValidationError) as serializer_exception:
            utils.custom_validate_email_function(CustomRegisterSerializer(), email)
        self.assertTrue(
            CustomValidationErrorText.VALIDATION_ERROR_EMAIL_MESSAGE_DOMAIN_SHORT in str(serializer_exception.exception)
        )
