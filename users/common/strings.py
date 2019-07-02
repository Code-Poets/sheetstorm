# pylint: disable=line-too-long
from enum import Enum

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from utils.mixins import NotCallableMixin


class ConfirmationMessages:
    SUCCESSFUL_UPDATE_USER_MESSAGE = _("Account has been successfully updated!")
    SUCCESSFUL_USER_PASSWORD_CHANGE_MESSAGE = _("Your password has been successfully updated!")
    FAILED_USER_PASSWORD_CHANGE_MESSAGE = _("Please correct the error below.")


class PermissionsMessage:
    NONE_ADMIN_USER = _("You are not allowed to enter - for administration only.")
    NONE_ADMIN_OR_OWNER_USER = _("It's none of your business.")


class CustomUserAdminText:
    PERSONAL_INFO = _("Personal info")
    STATUS = _("Status")
    PERMISSIONS = _("Permissions")
    IMPORTANT_DATES = _("Important dates")


class CustomUserModelText:
    VERBOSE_NAME_USER = _("user")
    VERBOSE_NAME_PLURAL_USERS = _("users")

    EMAIL_ADDRESS = _("email address")
    FIRST_NAME = _("first name")
    LAST_NAME = _("last name")
    IS_STAFF = _("staff status")
    STAFF_HELP_TEXT = _("Designates whether the user can log into this admin site.")
    IS_ACTIVE = _("active")
    ACTIVE_HELP_TEXT = _(
        "Designates whether this user should be treated as active. Unselect this instead of deleting accounts."
    )
    DATE_JOINED = _("date joined")
    DATE_OF_BIRTH = _("date of birth")
    UPDATED_AT = _("updated at")
    PHONE_REGEX_MESSAGE = _("Phone number must be entered in the format: '999999999'. Up to 15 digits allowed.")


class ValidationErrorText:
    VALIDATION_ERROR_EMAIL_MESSAGE = "Please enter correct email address"
    VALIDATION_ERROR_EMAIL_EXISTING_MESSAGE = "User with this Email address already exists."
    VALIDATION_ERROR_PASSWORD_MESSAGE = "Please enter your password"
    VALIDATION_ERROR_EMAIL_MALFORMED_FIRST_PART = "Invalid first part of email - you cannot use '' or ' ' signs"
    VALIDATION_ERROR_EMAIL_AT_SIGN_MESSAGE = 'The given email must contain one "@" sign'
    VALIDATION_ERROR_EMAIL_MESSAGE_DOMAIN = (
        "Please enter an e-mail address with a valid domain (" + ", ".join(settings.VALID_EMAIL_DOMAIN_LIST) + ")"
    )
    VALIDATION_ERROR_EMAIL_MESSAGE_DOMAIN_SHORT = "Please enter an e-mail address with a valid domain"
    VALIDATION_ERROR_SIGNUP_EMAIL_MESSAGE = _("A user is already registered with this e-mail address.")
    VALIDATION_ERROR_SIGNUP_PASSWORD_MESSAGE = _("The two password fields didn't match.")
    VALIDATION_ERROR_AGE_NOT_ACCEPTED = _("User can't be below 18 or above 99 years old.")


class CustomUserCountryText:
    POLAND = _("Poland")
    UNITED_STATES = _("United States")
    UNITED_KINGDOM = _("United Kingdom")
    GERMANY = _("Germany")
    FRANCE = _("France")


class CustomUserUserTypeText:
    EMPLOYEE = _("Employee")
    MANAGER = _("Manager")
    ADMIN = _("Admin")


class SuccessInfoAfterRegistrationText(NotCallableMixin, Enum):
    CONGRATULATIONS = _("Congratulations!")
    ACCOUNT_CREATED = _(
        "Your account has been successfully created! Please check your mailbox and activate your account!"
    )
    REDIRECTION_INFO = _("You will be redirected in few seconds to the login site or press a button to make it faster.")
    OKAY_BUTTON = _("Okay!")


class AccountConfirmationText(NotCallableMixin, Enum):
    SUCCESSFUL = _("Your account has been successfully activated! Now you can log in!")
    FAIL = _("Your account has not been activated! Please contact with contact@codepoets.it.")
    REDIRECTION_INFO = _("You will be redirected in few seconds to the login site or press a button to make it faster.")
    OKAY_BUTTON = _("Okay!")
