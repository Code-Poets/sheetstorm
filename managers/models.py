from typing import Any
from typing import Set

from django.db import models
from django.db.models import Q
from django.db.models.query import QuerySet
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from managers.commons.constants import MAX_NAME_LENGTH
from managers.commons.constants import MESSAGE_FOR_CORRECT_DATE_FORMAT
from users.models import CustomUser


class ProjectQuerySet(models.QuerySet):
    def filter_terminated(self) -> QuerySet:
        return self.filter(terminated=True, stop_date=None)

    def filter_active(self) -> QuerySet:
        return self.filter(terminated=False, stop_date=None)

    def filter_completed(self) -> QuerySet:
        return self.filter(~Q(stop_date=None))


class Project(models.Model):
    name = models.CharField(max_length=MAX_NAME_LENGTH)
    start_date = models.DateField(help_text=MESSAGE_FOR_CORRECT_DATE_FORMAT)
    stop_date = models.DateField(null=True, blank=True)
    terminated = models.BooleanField(default=False)
    managers = models.ManyToManyField(CustomUser, related_name="manager_projects")
    members = models.ManyToManyField(
        CustomUser, related_name="projects", help_text=_("How to add more employees? Select by CTRL + click")
    )

    objects = ProjectQuerySet.as_manager()

    def __str__(self) -> str:
        return self.name


@receiver(m2m_changed, sender=Project.managers.through)
def update_user_type(sender: Project, action: str, pk_set: Set, **kwargs: Any) -> None:
    assert sender == Project.managers.through
    project = kwargs["instance"]
    if action in ["pre_remove", "post_remove"]:
        change_user_type_to_employee(pk_set)
    elif action in ["pre_add", "post_add"]:
        change_user_type_to_manager(project)
    else:
        return


def change_user_type_to_manager(project: Project) -> None:
    for manager in project.managers.all():
        if manager.user_type == CustomUser.UserType.EMPLOYEE.name:
            manager.user_type = CustomUser.UserType.MANAGER.name
            manager.full_clean()
            manager.save()
        else:
            continue


def change_user_type_to_employee(pk_set: Set) -> None:
    for user_id in pk_set:
        user = CustomUser.objects.get(pk=user_id)
        if not user.manager_projects.exists() and user.user_type != CustomUser.UserType.ADMIN.name:
            user.user_type = CustomUser.UserType.EMPLOYEE.name
            user.full_clean()
            user.save()
        else:
            continue
