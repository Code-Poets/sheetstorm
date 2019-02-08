# pylint: disable=line-too-long
from django.utils.translation import ugettext_lazy
from users.common import constants


class CustomUserAdminText:
    PERSONAL_INFO = ugettext_lazy('Personal info')
    STATUS = ugettext_lazy('Status')
    PERMISSIONS = ugettext_lazy('Permissions')
    IMPORTANT_DATES = ugettext_lazy('Important dates')


class CustomUserModelText:
    VERBOSE_NAME_USER = ugettext_lazy('user')
    VERBOSE_NAME_PLURAL_USERS = ugettext_lazy('users')

    EMAIL_ADDRESS = ugettext_lazy('email address')
    FIRST_NAME = ugettext_lazy('first name')
    LAST_NAME = ugettext_lazy('last name')
    IS_STAFF = ugettext_lazy('staff status')
    STAFF_HELP_TEXT = ugettext_lazy('Designates whether the user can log into this admin site.')
    IS_ACTIVE = ugettext_lazy('active')
    ACTIVE_HELP_TEXT = ugettext_lazy('Designates whether this user should be treated as active. Unselect this instead of deleting accounts.')
    DATE_JOINED = ugettext_lazy('date joined')
    DATE_OF_BIRTH = ugettext_lazy('date of birth')
    UPDATED_AT = ugettext_lazy('updated at')
    PHONE_REGEX_MESSAGE = ugettext_lazy("Phone number must be entered in the format: '999999999'. Up to 15 digits allowed.")


class CustomValidationErrorText:
    VALIDATION_ERROR_EMAIL_MESSAGE = 'The given email must be set'
    VALIDATION_ERROR_PASSWORD_MESSAGE = 'The given password must be set'
    VALIDATION_ERROR_EMAIL_MESSAGE_DOMAIN = ugettext_lazy("Please enter an e-mail address with a valid domain (codepoets.it)")
    VALIDATION_ERROR_EMAIL_MALFORMED_FIRST_PART = "Invalid first part of email - you cannot use '' or ' ' signs"
    VALIDATION_ERROR_EMAIL_AT_SIGN_MESSAGE = 'The given email must contain one "@" sign'
    VALIDATION_ERROR_EMAIL_MESSAGE_DOMAIN = "Please enter an e-mail address with a valid domain (" + ', '.join(constants.VALID_EMAIL_DOMAIN_LIST) + ")"
    VALIDATION_ERROR_EMAIL_MESSAGE_DOMAIN_SHORT = "Please enter an e-mail address with a valid domain"
    VALIDATION_ERROR_SIGNUP_EMAIL_MESSAGE = ugettext_lazy("A user is already registered with this e-mail address.")
    VALIDATION_ERROR_SIGNUP_PASSWORD_MESSAGE = ugettext_lazy("The two password fields didn't match.")


class CustomUserCountryText:
    POLAND = ugettext_lazy('Poland')
    UNITED_STATES = ugettext_lazy('United States')
    UNITED_KINGDOM = ugettext_lazy('United Kingdom')
    GERMANY = ugettext_lazy('Germany')
    FRANCE = ugettext_lazy('France')


class CustomUserUserTypeText:
    EMPLOYEE = ugettext_lazy('Employee')
    MANAGER = ugettext_lazy('Manager')
    ADMIN = ugettext_lazy('Admin')
