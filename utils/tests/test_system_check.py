from unittest import TestCase

from django.conf import settings
from django.test import override_settings

from sheetstorm.system_check import check_settings_email_backend
from sheetstorm.system_check import check_settings_site_id
from sheetstorm.system_check import check_settings_valid_email_domain_list
from sheetstorm.system_check import create_error_01_valid_email_domain_list_is_not_a_list
from sheetstorm.system_check import create_error_02_invalid_domain_address
from sheetstorm.system_check import create_error_03_site_id_value_must_be_integer
from sheetstorm.system_check import create_error_04_email_backend_value_must_be_string
from sheetstorm.system_check import create_error_05_module_does_not_have_attribute
from sheetstorm.system_check import create_error_06_can_not_import_path
from sheetstorm.system_check import create_error_07_setting_does_not_exist
from sheetstorm.system_check import create_warning_01_duplicated_values_in_valid_email_domain_list
from sheetstorm.system_check import create_warning_02_empty_valid_email_domain_list


class TestValidEmailDomainList(TestCase):
    @override_settings(VALID_EMAIL_DOMAIN_LIST=["validdomain.it", "localhost"])
    def test_check_settings_valid_email_domain_list_with_correct_list(self):
        errors = check_settings_valid_email_domain_list()

        self.assertEqual(errors, [])

    @override_settings(VALID_EMAIL_DOMAIN_LIST=["duplicate.com", "duplicate.com"])
    def test_check_settings_valid_email_domain_list_warning_message_when_list_contains_duplicates(self):
        warnings = check_settings_valid_email_domain_list()

        self.assertTrue(len(warnings) == 1)
        self.assertEqual(warnings[0], create_warning_01_duplicated_values_in_valid_email_domain_list())

    @override_settings(VALID_EMAIL_DOMAIN_LIST=666)
    def test_check_settings_valid_email_domain_raise_error_when_it_is_not_instance_of_list(self):
        errors = check_settings_valid_email_domain_list()

        self.assertTrue(len(errors) == 1)
        self.assertEqual(errors[0], create_error_01_valid_email_domain_list_is_not_a_list())

    @override_settings(VALID_EMAIL_DOMAIN_LIST=[])
    def test_check_settings_valid_email_domain_warning_message_when_list_is_empty(self):
        warnings = check_settings_valid_email_domain_list()

        self.assertTrue(len(warnings) == 1)
        self.assertEqual(warnings[0], create_warning_02_empty_valid_email_domain_list())

    @override_settings(VALID_EMAIL_DOMAIN_LIST=["invaliddomain"])
    def test_check_settings_valid_email_domain_raise_error_when_domain_doesnt_have_dot(self):
        errors = check_settings_valid_email_domain_list()
        domain = settings.VALID_EMAIL_DOMAIN_LIST[0]

        self.assertTrue(len(errors) == 1)
        self.assertEqual(errors[0], create_error_02_invalid_domain_address(domain))

    @override_settings(VALID_EMAIL_DOMAIN_LIST=["code/@,poets.it"])
    def test_check_settings_valid_email_domain_raise_error_when_domain_contains_prohibited_signs(self):
        errors = check_settings_valid_email_domain_list()
        domain = settings.VALID_EMAIL_DOMAIN_LIST[0]

        self.assertTrue(len(errors) == 1)
        self.assertEqual(errors[0], create_error_02_invalid_domain_address(domain))

    @override_settings()
    def test_check_settings_valid_email_domain_list_raise_error_when_setting_does_not_exist(self):
        del settings.VALID_EMAIL_DOMAIN_LIST
        errors = check_settings_valid_email_domain_list()

        self.assertTrue(len(errors) == 1)
        self.assertEqual(errors[0], create_error_07_setting_does_not_exist("VALID_EMAIL_DOMAIN_LIST"))


class TestSiteId(TestCase):
    @override_settings(SITE_ID="STRING")
    def test_check_settings_site_id_raise_error_when_it_is_not_instance_of_integer(self):
        errors = check_settings_site_id()

        self.assertTrue(len(errors) == 1)
        self.assertEqual(errors[0], create_error_03_site_id_value_must_be_integer())

    @override_settings(SITE_ID=1)
    def test_check_site_id_with_correct_value(self):
        errors = check_settings_site_id()

        self.assertEqual(errors, [])

    @override_settings()
    def test_check_settings_site_id_raise_error_when_setting_does_not_exist(self):
        del settings.SITE_ID
        errors = check_settings_site_id()

        self.assertTrue(len(errors) == 1)
        self.assertEqual(errors[0], create_error_07_setting_does_not_exist("SITE_ID"))


class TestEmailBackend(TestCase):
    @override_settings(EMAIL_BACKEND="django.core.mail.backends.console.EmailBackend")
    def test_check_settings_email_backend_with_correct_path(self):
        errors = check_settings_email_backend()

        self.assertEqual(errors, [])

    @override_settings(EMAIL_BACKEND=[])
    def test_check_settings_email_backend_should_raise_error_when_it_is_not_instance_of_string(self):
        errors = check_settings_email_backend()

        self.assertTrue(len(errors) == 1)
        self.assertEqual(errors[0], create_error_04_email_backend_value_must_be_string())

    @override_settings(EMAIL_BACKEND="django.core.mail.notexistingmodule.console.EmailBackend")
    def test_check_settings_email_backend_should_raise_error_when_some_module_does_not_exist(self):
        errors = check_settings_email_backend()

        self.assertTrue(len(errors) == 1)
        self.assertEqual(errors[0], create_error_06_can_not_import_path("django.core.mail.notexistingmodule.console"))

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.console.NoAttribute")
    def test_check_settings_email_backend_should_raise_error_when_file_does_not_have_attribute(self):
        errors = check_settings_email_backend()

        self.assertTrue(len(errors) == 1)
        self.assertEqual(
            errors[0],
            create_error_05_module_does_not_have_attribute("django.core.mail.backends.console", "NoAttribute"),
        )

    @override_settings()
    def test_check_settings_email_backend_raise_error_when_setting_does_not_exist(self):
        del settings.EMAIL_BACKEND
        errors = check_settings_email_backend()

        self.assertTrue(len(errors) == 1)
        self.assertEqual(errors[0], create_error_07_setting_does_not_exist("EMAIL_BACKEND"))
