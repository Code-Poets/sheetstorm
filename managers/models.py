import logging
from typing import Any
from typing import Set

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Case
from django.db.models import Q
from django.db.models import Value
from django.db.models import When
from django.db.models.query import Prefetch
from django.db.models.query import QuerySet
from django.db.models.signals import m2m_changed
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from managers.commons.constants import ProjectConstants
from users.models import CustomUser

logger = logging.getLogger(__name__)


class ProjectQuerySet(models.QuerySet):
    def filter_suspended(self) -> QuerySet:
        return self.filter(suspended=True)

    def filter_active(self) -> QuerySet:
        return self.filter((Q(stop_date__gte=timezone.datetime.now()) | Q(stop_date__isnull=True)) & Q(suspended=False))

    def filter_completed(self) -> QuerySet:
        return self.filter(stop_date__lt=timezone.datetime.now())

    def get_with_prefetched_reports(self, reports: QuerySet) -> QuerySet:
        return self.prefetch_related(Prefetch("report_set", queryset=reports))


class Project(models.Model):
    name = models.CharField(max_length=ProjectConstants.MAX_NAME_LENGTH.value)
    start_date = models.DateField(help_text=ProjectConstants.MESSAGE_FOR_CORRECT_DATE_FORMAT.value)
    stop_date = models.DateField(null=True, blank=True)
    suspended = models.BooleanField(default=False)
    managers = models.ManyToManyField(CustomUser, related_name="manager_projects")
    members = models.ManyToManyField(CustomUser, related_name="projects")
    is_notification_enabled = models.BooleanField(default=True)

    objects = ProjectQuerySet.as_manager()

    def __str__(self) -> str:
        return self.name

    def get_report_ordered(self) -> QuerySet:
        return self.report_set.select_related("task_activities").order_by("author__email", "-date", "-creation_date")

    def clean(self) -> None:
        super().clean()
        if self.stop_date is not None and self.start_date > self.stop_date:
            raise ValidationError(message=ProjectConstants.STOP_DATE_VALIDATION_ERROR_MESSAGE.value)


@receiver(m2m_changed, sender=Project.managers.through)
def update_user_type(sender: Project, action: str, pk_set: Set, **kwargs: Any) -> None:
    assert sender == Project.managers.through
    project = kwargs["instance"]
    logger.debug(f"Updates on project with id: {sender.pk} for users with id: {pk_set}")
    if action == "post_remove":
        change_user_type_to_employee(pk_set)
    elif action == "post_add":
        change_user_type_to_manager(project)


def change_user_type_to_manager(project: Project) -> None:
    project.managers.filter(user_type=CustomUser.UserType.EMPLOYEE.name).update(
        user_type=CustomUser.UserType.MANAGER.name
    )


def change_user_type_to_employee(pk_set: Set) -> None:
    CustomUser.objects.filter(pk__in=pk_set).exclude(
        Q(user_type=CustomUser.UserType.ADMIN.name) | ~Q(manager_projects=None)
    ).update(user_type=CustomUser.UserType.EMPLOYEE.name)


@receiver(post_save, sender=Project)
def add_default_task_activities(sender: Project, **kwargs: Any) -> None:
    from employees.models import TaskActivityType

    assert sender == Project
    if kwargs["created"]:
        project = kwargs["instance"]

        project.project_activities.set(TaskActivityType.objects.get_defaults())


@receiver(post_save, sender=Project)
def change_suspended_if_project_has_stop_date(sender: Project, **kwargs: Any) -> None:
    assert sender == Project
    Project.objects.filter(pk=kwargs["instance"].pk).update(
        suspended=Case(
            When(Q(stop_date__lt=timezone.datetime.now()), then=Value(False)), default=kwargs["instance"].suspended
        )
    )
