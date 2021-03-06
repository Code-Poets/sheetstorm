import sys
from importlib import import_module
from importlib import util
from typing import Any

from django.conf import settings
from django.core.checks import Error
from django.core.checks import Warning  # pylint: disable=redefined-builtin
from django.core.checks import register

from common.constants import DOMAIN_REGEX


def create_error_01_valid_email_domain_list_is_not_a_list() -> Error:
    return Error("The value of VALID_EMAIL_DOMAIN_LIST setting is not a list", id="sheetstorm.E001")


def create_warning_01_duplicated_values_in_valid_email_domain_list() -> Warning:
    return Warning(
        "Some domains in VALID_EMAIL_DOMAIN_LIST are duplicated", hint="Remove duplicate domains", id="sheetstorm.W001"
    )


def create_error_02_invalid_domain_address(domain: str) -> Error:
    return Error(f"Domain {domain} should be valid url address", hint="Fix domain name.", id="sheetstorm.E002")


def create_warning_02_empty_valid_email_domain_list() -> Warning:
    return Warning(
        "VALID_EMAIL_DOMAIN_LIST settings does not contain any domain",
        hint="Add a valid domain to VALID_EMAIL_DOMAIN_LIST",
        id="sheetstorm.W002",
    )


def create_error_03_site_id_value_must_be_integer() -> Error:
    return Error("SITE_ID value must be an integer", id="sheetstorm.E004")


def create_error_04_email_backend_value_must_be_string() -> Error:
    return Error("EMAIL_BACKEND value must be a string", id="sheetstorm.E005")


def create_error_05_module_does_not_have_attribute(module: str, attribute: str) -> Error:
    return Error(f"Attribute {attribute} from module {module} doesn't exist", id="sheetstorm.E007")


def create_error_06_can_not_import_path(path: str) -> Error:
    return Error(f"Module from path: {path} can not be imported", id="sheetstorm.E008")


def create_error_07_setting_does_not_exist(setting: str) -> Error:
    return Error(f"{setting} is not declared in settings", id="sheetstorm.E010")


@register()
def check_settings_valid_email_domain_list(**kwargs: Any) -> list:  # pylint: disable=unused-argument
    if not hasattr(settings, "VALID_EMAIL_DOMAIN_LIST"):
        return [create_error_07_setting_does_not_exist("VALID_EMAIL_DOMAIN_LIST")]
    if not isinstance(settings.VALID_EMAIL_DOMAIN_LIST, list):
        return [create_error_01_valid_email_domain_list_is_not_a_list()]

    warnings = []
    if len(settings.VALID_EMAIL_DOMAIN_LIST) == 0:
        warnings.append(create_warning_02_empty_valid_email_domain_list())

    if len(set(settings.VALID_EMAIL_DOMAIN_LIST)) != len(settings.VALID_EMAIL_DOMAIN_LIST):
        warnings.append(create_warning_01_duplicated_values_in_valid_email_domain_list())

    for domain in settings.VALID_EMAIL_DOMAIN_LIST:
        if not DOMAIN_REGEX.match(domain):
            warnings.append(create_error_02_invalid_domain_address(domain))
    return warnings


@register()
def check_settings_site_id(**kwargs: Any) -> list:  # pylint: disable=unused-argument
    if not hasattr(settings, "SITE_ID"):
        return [create_error_07_setting_does_not_exist("SITE_ID")]
    if not isinstance(settings.SITE_ID, int):
        return [create_error_03_site_id_value_must_be_integer()]

    return []


@register()
def check_settings_email_backend(**kwargs: Any) -> list:  # pylint: disable=unused-argument
    if not hasattr(settings, "EMAIL_BACKEND"):
        return [create_error_07_setting_does_not_exist("EMAIL_BACKEND")]
    if not isinstance(settings.EMAIL_BACKEND, str):
        return [create_error_04_email_backend_value_must_be_string()]

    splitted_import_path = settings.EMAIL_BACKEND.split(".")
    path = settings.EMAIL_BACKEND.replace(".{}".format(splitted_import_path[-1]), "")

    try:
        imported_module = util.find_spec(path)
    except (ModuleNotFoundError, ValueError):
        return [create_error_06_can_not_import_path(path)]

    if imported_module is None:
        return [create_error_06_can_not_import_path(path)]
    try:
        import_module(imported_module.name)
        getattr(sys.modules[imported_module.name], splitted_import_path[-1])
    except AttributeError:
        return [create_error_05_module_does_not_have_attribute(imported_module.name, splitted_import_path[-1])]

    return []
