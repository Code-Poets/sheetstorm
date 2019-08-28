from django.core.exceptions import ValidationError
from django.test import TestCase
from django.test import override_settings
from parameterized import parameterized

from users.common.strings import ValidationErrorText
from users.validators import UserEmailValidation
from users.validators import UserNameValidatior


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


class TestUserNameValidator(TestCase):
    def setUp(self):
        self.user_name_validator = UserNameValidatior()

    @parameterized.expand(
        [
            "!",
            "@",
            "#",
            "$",
            "%",
            "^",
            "&",
            "*",
            "(",
            ")",
            "_",
            "+",
            "=",
            "/",
            "\\",
            "|",
            '"',
            "'",
            ":",
            ";",
            "{",
            "}",
            "[",
            "]",
            "/",
        ]
    )
    def test_validator_raise_exception_when_name_contains_special_characters(self, special_char):
        with self.assertRaises(ValidationError):
            self.user_name_validator(f"Kowalski{special_char}")

    def test_validator_should_pass_when_name_contain_dash(self):
        try:
            self.user_name_validator("Kowalska-Nowak")
        except ValidationError:
            self.fail()
