import logging
from datetime import date
from typing import Any
from typing import Optional

from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.mail import send_mail
from django.db import models
from django.db.models import Max
from django.db.models import Prefetch
from django.db.models import Q
from django.db.models import QuerySet
from django.db.models import Sum
from django.db.models import Value
from django.db.models.functions import Coalesce
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from users.common.constants import UserConstants
from users.common.fields import ChoiceEnum
from users.common.strings import CustomUserModelText
from users.common.strings import CustomUserUserTypeText
from users.common.strings import ValidationErrorText
from users.validators import UserEmailValidation
from users.validators import UserNameValidatior

logger = logging.getLogger(__name__)


class CustomUserQuerySet(models.QuerySet):
    def get_with_prefetched_reports(self, reports: QuerySet) -> QuerySet:
        return self.prefetch_related(Prefetch("report_set", queryset=reports))


class CustomUserManager(BaseUserManager):
    def _create_user(
        self, email: str, password: str, is_staff: bool, is_superuser: bool, user_type: str
    ) -> "CustomUser":
        """
        Creates and saves a user with the given email and password.
        Returns created user.
        """

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            password=password,
            is_staff=is_staff,
            is_active=True,
            is_superuser=is_superuser,
            user_type=user_type,
        )
        user.full_clean()
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email: str, password: str) -> "CustomUser":
        return self._create_user(
            email, password, is_staff=True, is_superuser=True, user_type=CustomUser.UserType.ADMIN.name
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
        max_length=UserConstants.EMAIL_MAX_LENGTH.value,
        unique=True,
        validators=[UserEmailValidation()],
        error_messages={"blank": ValidationErrorText.VALIDATION_ERROR_EMAIL_MESSAGE},
    )
    first_name = models.CharField(
        CustomUserModelText.FIRST_NAME,
        max_length=UserConstants.FIRST_NAME_MAX_LENGTH.value,
        blank=True,
        validators=[UserNameValidatior()],
    )
    last_name = models.CharField(
        CustomUserModelText.LAST_NAME,
        max_length=UserConstants.LAST_NAME_MAX_LENGTH.value,
        blank=True,
        validators=[UserNameValidatior()],
    )
    is_staff = models.BooleanField(
        CustomUserModelText.IS_STAFF, default=False, help_text=CustomUserModelText.STAFF_HELP_TEXT
    )
    is_active = models.BooleanField(
        CustomUserModelText.IS_ACTIVE, default=False, help_text=CustomUserModelText.ACTIVE_HELP_TEXT
    )
    date_joined = models.DateTimeField(CustomUserModelText.DATE_JOINED, auto_now_add=True)
    updated_at = models.DateTimeField(CustomUserModelText.UPDATED_AT, auto_now=True)
    user_type = models.CharField(
        max_length=UserConstants.USER_TYPE_MAX_LENGTH.value, choices=UserType.choices(), default=UserType.EMPLOYEE.name
    )
    password = models.CharField(
        max_length=128, error_messages={"null": ValidationErrorText.VALIDATION_ERROR_PASSWORD_MESSAGE}
    )
    objects = CustomUserManager.from_queryset(CustomUserQuerySet)()

    USERNAME_FIELD = "email"

    class Meta:
        verbose_name = CustomUserModelText.VERBOSE_NAME_USER
        verbose_name_plural = CustomUserModelText.VERBOSE_NAME_PLURAL_USERS
        ordering = ("id",)

    def get_absolute_url(self) -> str:
        """
        Returns the absolute url with user's email.
        example: /users/admin@example.com
        """
        return "/users/%s/" % self.email

    def get_full_name(self) -> str:
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self) -> str:
        """
        Returns the short name for the user.
        """
        return self.first_name

    def email_user(self, subject: str, message: str, from_email: str = None) -> None:
        """
        Sends an email to this user.
        """
        send_mail(subject, message, from_email, [self.email])

    @property
    def is_admin(self) -> bool:
        return self.user_type == CustomUser.UserType.ADMIN.name

    @property
    def is_manager(self) -> bool:
        return self.user_type == CustomUser.UserType.MANAGER.name

    @property
    def is_employee(self) -> bool:
        return self.user_type == CustomUser.UserType.EMPLOYEE.name

    def get_reports_created(self) -> QuerySet:
        return self.report_set.select_related("task_activities").order_by("-date", "project__name")

    def get_projects_work_percentage(self, from_date: Optional[date] = None, to_date: Optional[date] = None) -> dict:
        """
        Returns dict where keys are Project objects and values are percentage amount of work
        by this user between given dates.
        """
        if from_date is None:
            from_date = timezone.now().date().replace(day=1)
        if to_date is None:
            to_date = timezone.now().date()

        work_hours_per_project = self.projects.filter(report__date__range=[from_date, to_date]).annotate(
            work_hours_sum=Coalesce(Sum("report__work_hours", filter=Q(report__author=self)), timezone.timedelta())
        )
        work_hours_sum = work_hours_per_project.aggregate(
            sum_work_hours_sum=Coalesce(Sum("work_hours_sum"), timezone.timedelta())
        )["sum_work_hours_sum"]

        return {
            project: ((project.work_hours_sum / work_hours_sum) * 100 if work_hours_sum.total_seconds() > 0 else 0)
            for project in work_hours_per_project
        }

    def get_project_ordered_by_last_report_creation_date(self) -> QuerySet:
        return self.projects.annotate(
            last_report_creation_date=Coalesce(
                Max("report__creation_date", filter=Q(report__author=self)), Value("1970-01-01 00:00:00")
            )
        ).order_by("-last_report_creation_date")


@receiver(post_save, sender=CustomUser)
def update_from_manager_to_employee(sender: "CustomUser", **kwargs: Any) -> None:
    user = kwargs["instance"]
    logger.debug(f"Update user: {user.pk} from manager to employee")
    assert sender == CustomUser
    if user.user_type == CustomUser.UserType.EMPLOYEE.name:
        logger.debug(f"User: {user.pk} has been deleted from all projects")
        user.manager_projects.clear()
    else:
        return
