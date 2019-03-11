from django.db import models
from django.db.models import Q
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from managers.commons.constants import MAX_NAME_LENGTH
from users.common.strings import CustomUserUserTypeText
from users.models import CustomUser


class ProjectQuerySet(models.QuerySet):
    def filter_terminated(self):
        return self.filter(terminated=True, stop_date=None)

    def filter_active(self):
        return self.filter(terminated=False, stop_date=None)

    def filter_completed(self):
        return self.filter(~Q(stop_date=None))


class Project(models.Model):
    name = models.CharField(max_length=MAX_NAME_LENGTH)
    start_date = models.DateField()
    stop_date = models.DateField(null=True, blank=True)
    terminated = models.BooleanField(default=False)
    managers = models.ManyToManyField(CustomUser, related_name="manager_projects")
    members = models.ManyToManyField(CustomUser, related_name="projects")

    objects = ProjectQuerySet.as_manager()

    def __str__(self):
        return self.name


@receiver(m2m_changed, sender=Project.managers.through)
def update_user_type(sender, action, pk_set, **kwargs):
    project = kwargs['instance']
    if action == 'pre_remove' or action == 'post_remove':
        change_user_type_to_employee(pk_set)
    elif action == 'pre_add' or action == "post_add":
        change_user_type_to_manager(project)
    else:
        return


def change_user_type_to_manager(project):
    for manager in project.managers.all():
        if manager.user_type != CustomUser.UserType.MANAGER.name:
            manager.user_type = CustomUser.UserType.MANAGER.name
            manager.full_clean()
            manager.save()
        else:
            return


def change_user_type_to_employee(pk_set):
    for user_id in pk_set:
        user = CustomUser.objects.get(pk=user_id)
        if not user.manager_projects.exists():
            user.user_type = CustomUser.UserType.EMPLOYEE.name
            user.full_clean()
            user.save()
        else:
            return
