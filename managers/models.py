import logging
from typing import Any
from typing import Set

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.db.models.query import QuerySet
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from managers.commons.constants import ProjectConstants
from users.models import CustomUser

logger = logging.getLogger(__name__)


class ProjectQuerySet(models.QuerySet):
    def filter_terminated(self) -> QuerySet:
        return self.filter(terminated=True, stop_date=None)

    def filter_active(self) -> QuerySet:
        return self.filter(terminated=False, stop_date=None)

    def filter_completed(self) -> QuerySet:
        return self.filter(~Q(stop_date=None))


class Project(models.Model):
    name = models.CharField(max_length=ProjectConstants.MAX_NAME_LENGTH.value)
    start_date = models.DateField(help_text=ProjectConstants.MESSAGE_FOR_CORRECT_DATE_FORMAT.value)
    stop_date = models.DateField(null=True, blank=True)
    terminated = models.BooleanField(default=False)
    managers = models.ManyToManyField(CustomUser, related_name="manager_projects")
    members = models.ManyToManyField(CustomUser, related_name="projects")

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
    if action in ["pre_remove", "post_remove"]:
        change_user_type_to_employee(pk_set)
    elif action in ["pre_add", "post_add"]:
        change_user_type_to_manager(project)
    else:
        return


def change_user_type_to_manager(project: Project) -> None:
    for manager in project.managers.all():
        logger.debug(f"User with user type: {manager.user_type} with id: {manager.pk} in managers")
        if manager.user_type == CustomUser.UserType.EMPLOYEE.name:
            logger.debug(
                f"User with user type: {manager.user_type} and id: {manager.pk} is in managers for project with id: {project.pk}"
            )
            manager.user_type = CustomUser.UserType.MANAGER.name
            manager.full_clean()
            manager.save()
            logger.debug(f"User with id: {manager.pk} have changed user type to manager")
        else:
            continue


def change_user_type_to_employee(pk_set: Set) -> None:
    for user_id in pk_set:
        user = CustomUser.objects.get(pk=user_id)
        if not user.manager_projects.exists() and user.user_type != CustomUser.UserType.ADMIN.name:
            logger.info(f"User: {user} user type change to employee")
            user.user_type = CustomUser.UserType.EMPLOYEE.name
            user.full_clean()
            user.save()
            logger.info(f"User with id: {user.pk} have changed user type to employee")
        else:
            logger.debug(f"User with id: {user.pk} has not changed to employee")
            continue
