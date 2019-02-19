from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.mail import send_mail
from django.db import models
from django_countries.fields import CountryField

from users.common import constants
from users.common.constants import ErrorCode
from users.common.exceptions import CustomValidationError
from users.common.fields import ChoiceEnum
from users.common.strings import CustomUserModelText
from users.common.strings import CustomUserUserTypeText
from users.common.strings import CustomValidationErrorText
from users.common.utils import custom_validate_email_function
from users.common.validators import PhoneRegexValidator


class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(
        self,
        email,
        password,
        is_staff,
        is_superuser,
        user_type,
    ):
        """
        Creates and saves a user with the given email and password.
        Returns created user.
        """

        if email is None:
            raise CustomValidationError(
                CustomValidationErrorText.VALIDATION_ERROR_EMAIL_MESSAGE,
                ErrorCode.CREATE_USER_EMAIL_MISSING,
            )
        else:
            custom_validate_email_function(self, email)

        if not password:
            raise CustomValidationError(
                CustomValidationErrorText.VALIDATION_ERROR_PASSWORD_MESSAGE,
                ErrorCode.CREATE_USER_PASSWORD_MISSING,
            )
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            is_staff=is_staff,
            is_active=True,
            is_superuser=is_superuser,
            user_type=user_type,
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(
        self,
        email,
        password,
    ):
        return self._create_user(
            email,
            password,
            is_staff=True,
            is_superuser=True,
            user_type=CustomUser.UserType.ADMIN.name,
        )


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    A fully featured User model with admin-compliant permissions that uses
    a full-length email field as the username.

    Email and password are required. Other fields are optional.
    """

    class UserType(ChoiceEnum):
        EMPLOYEE = CustomUserUserTypeText.EMPLOYEE
        MANAGER = CustomUserUserTypeText.MANAGER
        ADMIN = CustomUserUserTypeText.ADMIN

    email = models.EmailField(
        CustomUserModelText.EMAIL_ADDRESS,
        max_length=constants.EMAIL_MAX_LENGTH,
        unique=True,
    )
    first_name = models.CharField(
        CustomUserModelText.FIRST_NAME,
        max_length=constants.FIRST_NAME_MAX_LENGTH,
        blank=True,
    )
    last_name = models.CharField(
        CustomUserModelText.LAST_NAME,
        max_length=constants.LAST_NAME_MAX_LENGTH,
        blank=True,
    )
    is_staff = models.BooleanField(
        CustomUserModelText.IS_STAFF,
        default=False,
        help_text=CustomUserModelText.STAFF_HELP_TEXT,
    )
    is_active = models.BooleanField(
        CustomUserModelText.IS_ACTIVE,
        default=True,
        help_text=CustomUserModelText.ACTIVE_HELP_TEXT,
    )
    date_joined = models.DateTimeField(
        CustomUserModelText.DATE_JOINED,
        auto_now_add=True,
    )
    date_of_birth = models.DateField(
        CustomUserModelText.DATE_OF_BIRTH,
        blank=True,
        null=True,
    )
    updated_at = models.DateTimeField(
        CustomUserModelText.UPDATED_AT,
        auto_now=True,
    )
    phone_number = models.CharField(
        validators=[PhoneRegexValidator],
        max_length=constants.PHONE_NUMBER_MAX_LENGTH,
        blank=True,
        null=True,
    )
    country = CountryField(blank=True)
    user_type = models.CharField(
        max_length=constants.USER_TYPE_MAX_LENGTH,
        choices=UserType.choices(),
        default=UserType.EMPLOYEE.name,
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = CustomUserModelText.VERBOSE_NAME_USER
        verbose_name_plural = CustomUserModelText.VERBOSE_NAME_PLURAL_USERS
        ordering = ('id',)

    def clean(self):
        custom_validate_email_function(self, self.email)

    def get_absolute_url(self):
        """
        Returns the absolute url with user's email.
        example: /users/admin@example.com
        """
        return "/users/%s/" % self.email

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self):
        """
        Returns the short name for the user.
        """
        return self.first_name

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this user.
        """
        send_mail(subject, message, from_email, [self.email])
